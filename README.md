# Pakkada Data Collection — Django Setup Guide

## Prerequisites
- Python 3.8+
- PostgreSQL running locally (or any accessible host)

---

## 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

---

## 2. Database

SQLite3 is used — **no setup required**. The database file `db.sqlite3` is created automatically on first migrate.

---

## 3. Run Migrations

```bash
python3 manage.py migrate
```

---

## 4. Create Superuser (optional, for admin panel)

```bash
python3 manage.py createsuperuser
```

---

## 5. Start the Development Server

```bash
python3 manage.py runserver
```

Open your browser at **http://127.0.0.1:8000**

---

## URL Routes

| URL              | Description                      |
|------------------|----------------------------------|
| `/`              | List all family submissions      |
| `/new/`          | Data entry form                  |
| `/<id>/`         | Detail view with pretty JSON     |
| `/admin/`        | Django admin panel               |

---

## Project Structure

```
pakkada_data_collection/
├── manage.py
├── requirements.txt
├── README.md
│
├── pakkada/                    # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── family/                     # Main app
│   ├── models.py               # Family model (JSONField)
│   ├── views.py                # List, Create, Detail views
│   ├── urls.py                 # App URL patterns
│   ├── admin.py                # Admin registration
│   ├── apps.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── static/
│   │   └── js/
│   │       └── form_dynamic.js # Dynamic form JS (no framework)
│   └── templates/family/
│       ├── form.html           # Main entry form
│       ├── list.html           # All submissions table
│       ├── detail.html         # Pretty JSON viewer
│       └── success.html
│
└── templates/
    └── base.html               # Base layout (Bootstrap 5)
```

---

## JSON Storage Format

Each submission stores exactly this structure in `Family.family_json`:

```json
{
  "പഞ്ചായത്ത്": "...",
  "വാർഡ്": "...",
  "ഫോം നമ്പർ": "...",
  "ഗൃഹനാഥന്റെ പേര്": "...",
  "മൊബൈൽ നമ്പർ": "...",
  "ഉപ്പയുടെ പേര്": "...",
  "ഉമ്മയുടെ പേര്": "...",
  "ഭാര്യയുടെ പേര്": "...",
  "മക്കളുടെ വിവരം": [
    {
      "ബന്ധം": "മകൻ",
      "പേര്": "...",
      "മൊബൈൽ നമ്പർ": "...",
      "ഭാര്യയുടെ പേര്": "...",
      "കുട്ടികൾ": { "5 വയസിനു മുകളിൽ": 0, "5 വയസിനു താഴെ": 0 }
    }
  ],
  "സഹോദരിമാരുടെ വിവരങ്ങൾ": [
    {
      "സഹോദരിയുടെ പേര്": "...",
      "മൊബൈൽ നമ്പർ": "...",
      "കുട്ടികൾ": { "5 വയസിനു മുകളിൽ": 0, "5 വയസിനു താഴെ": 0 }
    }
  ]
}
```

> `ഭാര്യയുടെ പേര്` key is included **only** when `ബന്ധം = "മകൻ"`.
