# TANAXIS AI

TANAXIS AI, TANAXIS markası için geliştirilmiş yapay zekâ destekli bir web uygulamasıdır.

Proje; Flask tabanlı bir backend, Groq yapay zekâ servisi, SQLite veritabanı, Render deployment ve Wix Studio kullanıcı arayüzünü bir araya getirir.

## Projenin Amacı

TANAXIS; şehir planlama, tasarım, mekânsal veri, kentsel gelişim, danışmanlık ve eğitim alanlarında faaliyet gösteren disiplinlerarası bir üretim markasıdır.

Bu proje ile ziyaretçilerin:

- TANAXIS hakkında yapay zekâ destekli bilgi alması,
- Hizmetler hakkında soru sorabilmesi,
- İletişim bilgilerini bırakabilmesi,
- Bırakılan müşteri adaylarının yönetim ekranından görüntülenebilmesi

amaçlanmıştır.

## Kullanılan Teknolojiler

- Python
- Flask
- Flask-CORS
- SQLite
- Groq API
- Wix Studio / Velo
- Render
- Git & GitHub

## Proje Mimarisi

```text
tanaxisai/
│
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   └── ai_service.py
│   ├── templates/
│   │   ├── index.html
│   │   └── dashboard.html
│   ├── __init__.py
│   ├── database.py
│   └── routes.py
│
├── config.py
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```

## API Endpointleri

### Ana Sayfa

```http
GET /
```

### Dashboard

```http
GET /dashboard
```

### Yapay Zekâ Sohbeti

```http
POST /api/sohbet
```

Örnek istek:

```json
{
  "mesaj": "TANAXIS nedir?",
  "gecmis": []
}
```

### Müşteri Adayı Kaydetme

```http
POST /api/leads
```

### Müşteri Adaylarını Listeleme

```http
GET /api/leads
```

### Sistem Sağlık Kontrolü

```http
GET /health
GET /healthz
```

## Yapay Zekâ Entegrasyonu

Uygulamanın yapay zekâ servisi Groq API üzerinden çalışmaktadır.

Kullanılan model:

```text
openai/gpt-oss-20b
```

API anahtarı güvenlik nedeniyle `.env` dosyasında tutulmaktadır ve GitHub reposuna gönderilmemektedir.

## Veritabanı

Projede SQLite kullanılmaktadır.

Müşteri adayları aşağıdaki temel bilgilerle kaydedilmektedir:

- ID
- İsim
- Telefon
- Mesaj / e-posta bilgisi
- Kayıt tarihi

SQL işlemleri `database.py` içerisinde gerçekleştirilmektedir ve sorgularda parametreli SQL kullanılmaktadır.

## Wix Studio Entegrasyonu

Wix Studio projenin kullanıcı arayüzü olarak kullanılmaktadır.

Ziyaretçi arayüzü üzerinden kullanıcılar TANAXIS AI ile iletişim kurabilir ve iletişim bilgilerini bırakabilir.

Yönetim arayüzü üzerinden kaydedilen müşteri adayları görüntülenebilir.

Wix Velo ile Flask API arasında HTTP istekleri kullanılarak veri alışverişi gerçekleştirilmektedir.

## Deployment

Backend Render üzerinde yayınlanmıştır.

Backend adresi:

```text
https://tanaxis-ai.onrender.com
```

Sağlık kontrolü:

```text
https://tanaxis-ai.onrender.com/healthz
```

Wix Studio sitesi:

```text
https://thaliltopcu.wixstudio.com/tanaxis
```

## Yerel Çalıştırma

Sanal ortamı etkinleştirdikten sonra:

```bash
pip install -r requirements.txt
python run.py
```

Uygulama varsayılan olarak:

```text
http://127.0.0.1:5000
```

adresinde çalışır.

## Güvenlik

Groq API anahtarı kaynak kod içerisinde tutulmamaktadır.

`.env`, sanal ortam, SQLite veritabanı ve geçici Python dosyaları `.gitignore` ile GitHub dışında bırakılmıştır.

## Sistem Akışı

```text
Kullanıcı
   ↓
Wix Studio
   ↓
Flask REST API
   ├── Groq API → Yapay zekâ yanıtı
   └── SQLite → Müşteri adayları
   ↓
JSON Response
   ↓
Wix Studio
```

## Geliştirici

Halil Topçu

TANAXIS AI — 2026