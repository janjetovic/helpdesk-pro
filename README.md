# 🎫 HelpDesk Pro — IT-Support-Ticketsystem

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/Lizenz-MIT-green?style=flat-square)

**Ein vollständiges IT-Ticketsystem mit Rollenverwaltung, Dashboard und Echtzeit-Statistiken.**

[Funktionen](#-funktionen) · [Installation](#-installation) · [Verwendung](#-verwendung) · [API](#-api-endpunkte) · [Technologien](#-technologien)

</div>

---

## 📋 Überblick

**HelpDesk Pro** ist ein webbasiertes IT-Support-Ticketsystem, das den gesamten Lebenszyklus eines Support-Tickets abbildet — von der Erstellung durch einen Mitarbeiter bis zur Lösung durch das IT-Team.

Das System umfasst eine Rollenverwaltung (Admin, Techniker, Mitarbeiter), ein Dashboard mit Statistiken, eine Kommentarfunktion und ein konfigurierbares Alarm-System für Tickets mit hoher Priorität.

Dieses Projekt demonstriert praxisrelevante Konzepte der **IT-Administration** und **Anwendungsentwicklung** — relevante Kernkompetenzen für den Ausbildungsberuf **Fachinformatiker Systemintegration**.

## ✨ Funktionen

### Ticket-Verwaltung
- **Tickets erstellen** — Titel, Beschreibung, Kategorie und Priorität
- **Status-Workflow** — Offen → In Bearbeitung → Wartend → Geschlossen
- **Prioritäten** — Niedrig, Mittel, Hoch, Kritisch
- **Kategorien** — Hardware, Software, Netzwerk, Zugang/Berechtigungen, Sonstiges
- **Kommentare** — Kommunikation zwischen Mitarbeitern und Technikern
- **Interne Notizen** — Nur für das IT-Team sichtbar
- **Filter & Suche** — Tickets nach Status, Priorität, Kategorie filtern

### Benutzerverwaltung
- **Drei Rollen** — Admin (voller Zugriff), Techniker (Ticket-Bearbeitung), Mitarbeiter (eigene Tickets)
- **Authentifizierung** — Session-basiertes Login mit gehashten Passwörtern
- **Zugriffskontrolle** — Rollenbasierte Berechtigungen für alle Funktionen

### Dashboard
- **Statistik-Karten** — Übersicht offener, laufender und gelöster Tickets
- **Diagramme** — Tickets nach Status und Kategorie (Chart.js)
- **Alarm-Banner** — Warnung bei kritischen/hohen offenen Tickets
- **Schnellzugriff** — Neueste Tickets und zugewiesene Aufgaben

### Technisch
- **REST-API** — JSON-Endpunkte für alle Statistikdaten
- **SQLite-Datenbank** — Keine externe Datenbank erforderlich
- **Docker-Unterstützung** — Ein-Befehl-Deployment
- **Unit-Tests** — 20+ automatisierte Tests
- **Demodaten** — Vorkonfigurierte Benutzer und Beispiel-Tickets

## 🚀 Installation

### Voraussetzungen
- Python 3.10 oder höher
- pip (Python-Paketmanager)
- Optional: Docker & Docker Compose

### Option 1: Lokale Installation

```bash
git clone https://github.com/DEIN-BENUTZERNAME/helpdesk-pro.git
cd helpdesk-pro
pip install -r requirements.txt
python run.py
```

Das Dashboard ist dann unter **http://localhost:5000** erreichbar.

### Option 2: Mit Docker

```bash
docker-compose up -d
```

### Option 3: Virtuelle Umgebung

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

## 💻 Verwendung

### Demo-Zugangsdaten

| Rolle | Benutzername | Passwort | Berechtigungen |
|---|---|---|---|
| **Admin** | `admin` | `admin123` | Voller Zugriff, Benutzerverwaltung |
| **Techniker** | `technik1` | `tech123` | Tickets bearbeiten, zuweisen, kommentieren |
| **Mitarbeiter** | `mueller` | `user123` | Eigene Tickets erstellen und einsehen |

### Workflow

1. **Mitarbeiter** erstellt ein Ticket mit Problembeschreibung
2. **Techniker** sieht das Ticket im Dashboard und weist es sich zu
3. **Techniker** ändert den Status auf "In Bearbeitung" und kommentiert
4. Nach Lösung wird das Ticket auf "Geschlossen" gesetzt

## 📡 API-Endpunkte

| Endpunkt | Methode | Beschreibung |
|---|---|---|
| `/api/health` | GET | Gesundheitsprüfung |
| `/api/stats/overview` | GET | Dashboard-Statistiken (Auth erforderlich) |

## 🧪 Tests

```bash
python -m unittest tests.test_helpdesk -v
```

Die Testsuite umfasst Tests für Authentifizierung, Ticket-CRUD, Kommentare, Zugriffskontrolle, API und Datenbankmodelle.

## 🛠️ Technologien

| Technologie | Einsatz |
|---|---|
| **Python 3** | Backend-Logik und API |
| **Flask** | Web-Framework |
| **SQLAlchemy** | ORM für Datenbankzugriff |
| **Flask-Login** | Authentifizierung und Sessions |
| **SQLite** | Datenbank (kein externer Server nötig) |
| **Chart.js** | Dashboard-Diagramme |
| **HTML/CSS/JS** | Frontend |
| **Docker** | Container-Deployment |

## 📁 Projektstruktur

```
helpdesk-pro/
├── app/
│   ├── __init__.py
│   ├── main.py              # Flask-App, Routen, Authentifizierung
│   ├── models.py            # Datenbankmodelle (User, Ticket, Comment)
│   └── seed.py              # Demodaten-Generator
├── static/
│   └── css/style.css        # Professionelles SaaS-Design
├── templates/
│   ├── base.html            # Basis-Layout mit Sidebar
│   ├── login.html           # Anmeldeseite
│   ├── dashboard.html       # Dashboard mit Statistiken
│   ├── tickets.html         # Ticket-Liste mit Filtern
│   ├── ticket_detail.html   # Ticket-Detailansicht
│   ├── ticket_form.html     # Neues Ticket erstellen
│   ├── users.html           # Benutzerverwaltung (Admin)
│   └── error.html           # Fehlerseite
├── tests/
│   └── test_helpdesk.py     # Unit-Tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py                   # Startskript
├── LICENSE
└── README.md
```

## ⚙️ Konfiguration

| Variable | Standard | Beschreibung |
|---|---|---|
| `HELPDESK_HOST` | `0.0.0.0` | Host-Adresse |
| `HELPDESK_PORT` | `5000` | Port-Nummer |
| `HELPDESK_DEBUG` | `false` | Debug-Modus |
| `SECRET_KEY` | dev-key | Session-Verschlüsselung |

## 📄 Lizenz

Dieses Projekt steht unter der [MIT-Lizenz](LICENSE).

---

<div align="center">
Entwickelt mit 🎫 als Praxisprojekt für Fachinformatiker Systemintegration
</div>
