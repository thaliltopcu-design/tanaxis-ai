from flask import Blueprint, jsonify, render_template, request
import csv
import io
import os
import smtplib
from email.message import EmailMessage

from app.database import lead_ekle, tum_leadler
from app.services.ai_service import AIServiceError, ai_service


pages_bp = Blueprint("pages", __name__)
api_bp = Blueprint("api", __name__)

def lead_mail_gonder(isim, telefon, mesaj):
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_receiver = os.getenv("MAIL_RECEIVER")

    if not mail_username or not mail_password or not mail_receiver:
        return

    email = EmailMessage()
    email["Subject"] = f"TANAXIS | Yeni Lead - {isim}"
    email["From"] = mail_username
    email["To"] = mail_receiver

    email.set_content(
        f"""TANAXIS sistemine yeni bir lead kaydı geldi.

İsim: {isim}
Telefon: {telefon}

Başvuru / Talep Bilgileri:
{mesaj}

---
Bu e-posta TANAXIS Lead Sistemi tarafından otomatik gönderilmiştir.
"""
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(mail_username, mail_password)
        smtp.send_message(email)

@pages_bp.route("/")
def index():
    return render_template("index.html")


@pages_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@api_bp.route("/sohbet", methods=["POST"])
def sohbet():
    data = request.get_json(silent=True) or {}

    mesaj = data.get("mesaj", "").strip()
    gecmis = data.get("gecmis", [])

    if not mesaj:
        return jsonify(
            {
                "basari": False,
                "hata": "Mesaj alani bos birakilamaz."
            }
        ), 400

    try:
        cevap = ai_service.yanit_uret(mesaj, gecmis)

        return jsonify(
            {
                "basari": True,
                "cevap": cevap
            }
        ), 200

    except AIServiceError as exc:
        return jsonify(
            {
                "basari": False,
                "hata": str(exc)
            }
        ), 503


@api_bp.route("/leads", methods=["POST"])
def lead_kaydet():
    data = request.get_json(silent=True) or {}

    isim = data.get("isim", "").strip()
    telefon = data.get("telefon", "").strip()
    mesaj = data.get("mesaj", "").strip()

    if not isim or not telefon:
        return jsonify(
            {
                "basari": False,
                "hata": "Isim ve telefon alanlari zorunludur."
            }
        ), 400

    try:
        lead_id = lead_ekle(
            isim=isim,
            telefon=telefon,
            mesaj=mesaj
        )

        try:
            lead_mail_gonder(isim, telefon, mesaj)
        except Exception as mail_hatasi:
            print(f"Lead kaydedildi ancak e-posta gonderilemedi: {mail_hatasi}")

        return jsonify(
            {
                "basari": True,
                "mesaj": "Iletisim bilginiz basariyla kaydedildi.",
                "lead_id": lead_id
            }
        ), 201

    except Exception:
        return jsonify(
            {
                "basari": False,
                "hata": "Kayit sirasinda bir hata olustu."
            }
        ), 500


@api_bp.route("/leads", methods=["GET"])
def leadleri_listele():
    try:
        leads = tum_leadler()

        return jsonify(
            {
                "basari": True,
                "leads": leads
            }
        ), 200

    except Exception:
        return jsonify(
            {
                "basari": False,
                "hata": "Kayitlar getirilirken bir hata olustu."
            }
        ), 500
@api_bp.route("/leads/csv", methods=["GET"])
def leadleri_csv_indir():
    try:
        leads = tum_leadler()

        output = io.StringIO()
        output.write("\ufeff")  # Excel'de Türkçe karakterler düzgün açılsın

        writer = csv.writer(output)
        writer.writerow(["ID", "İsim", "Telefon", "Mesaj", "Tarih"])

        for lead in leads:
            writer.writerow([
                lead.get("id", ""),
                lead.get("isim", ""),
                lead.get("telefon", ""),
                lead.get("mesaj", ""),
                lead.get("tarih", "")
            ])

        return output.getvalue(), 200, {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition": "attachment; filename=TANAXIS_lead_kayitlari.csv"
        }

    except Exception:
        return jsonify({
            "basari": False,
            "hata": "CSV dosyasi olusturulurken bir hata olustu."
        }), 500
