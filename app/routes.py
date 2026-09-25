from flask import Blueprint, jsonify, render_template, request
import csv
import io
import os
import requests

from app.database import lead_ekle, tum_leadler
from app.services.ai_service import AIServiceError, ai_service


pages_bp = Blueprint("pages", __name__)
api_bp = Blueprint("api", __name__)

def lead_mail_gonder(isim, telefon, mesaj):
    api_key = os.getenv("RESEND_API_KEY")

    if not api_key:
        return

    try:
        requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "from": "TANAXIS Lead <onboarding@resend.dev>",
                "to": ["tanaxis.co@gmail.com"],
                "subject": f"TANAXIS | Yeni Lead - {isim}",
                "text": f"""TANAXIS sistemine yeni bir lead kaydi geldi.

Isim: {isim}
Telefon: {telefon}

Basvuru / Talep Bilgileri:
{mesaj}

---
Bu e-posta TANAXIS Lead Sistemi tarafindan otomatik gonderilmistir.
"""
            },
            timeout=5
        )
    except requests.RequestException as hata:
        print(f"Lead e-postasi gonderilemedi: {hata}")

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
        
        lead_mail_gonder(isim, telefon, mesaj)
        
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
