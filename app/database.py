import sqlite3
from flask import current_app, g


def get_db():
    """Aktif SQLite veritabani baglantisini dondurur."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(error=None):
    """Istek tamamlandiginda veritabani baglantisini kapatir."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db(app):
    """Leads tablosunu yoksa olusturur."""
    with app.app_context():
        db = get_db()

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isim TEXT NOT NULL,
                telefon TEXT NOT NULL,
                mesaj TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        db.commit()

    app.teardown_appcontext(close_db)


def lead_ekle(isim, telefon, mesaj=None):
    """Yeni bir musteri adayini veritabanina kaydeder."""
    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO leads (isim, telefon, mesaj)
        VALUES (?, ?, ?)
        """,
        (isim, telefon, mesaj),
    )

    db.commit()

    return cursor.lastrowid


def tum_leadler():
    """Tum musteri adaylarini en yeniden eskiye getirir."""
    db = get_db()

    rows = db.execute(
        """
        SELECT id, isim, telefon, mesaj, tarih
        FROM leads
        ORDER BY id DESC
        """
    ).fetchall()

    return [dict(row) for row in rows]