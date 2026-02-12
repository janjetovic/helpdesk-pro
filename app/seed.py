"""
HelpDesk Pro - Demodaten
Erstellt Beispiel-Benutzer und Tickets für die erste Nutzung.
"""

from datetime import datetime, timedelta
import random
from app.models import db, User, Ticket, Comment


def seed_database():
    """Erstellt Demodaten, falls die Datenbank leer ist."""
    if User.query.first() is not None:
        return

    # ── Benutzer erstellen ──────────────────────────
    admin = User(
        username="admin",
        email="admin@firma.de",
        full_name="Max Müller",
        role="admin",
        department="IT-Abteilung",
    )
    admin.set_password("admin123")

    tech1 = User(
        username="technik1",
        email="technik1@firma.de",
        full_name="Laura Schmidt",
        role="techniker",
        department="IT-Abteilung",
    )
    tech1.set_password("tech123")

    tech2 = User(
        username="technik2",
        email="technik2@firma.de",
        full_name="Jonas Weber",
        role="techniker",
        department="IT-Abteilung",
    )
    tech2.set_password("tech123")

    user1 = User(
        username="mueller",
        email="s.mueller@firma.de",
        full_name="Sabine Müller",
        role="mitarbeiter",
        department="Buchhaltung",
    )
    user1.set_password("user123")

    user2 = User(
        username="fischer",
        email="t.fischer@firma.de",
        full_name="Thomas Fischer",
        role="mitarbeiter",
        department="Vertrieb",
    )
    user2.set_password("user123")

    user3 = User(
        username="becker",
        email="a.becker@firma.de",
        full_name="Anna Becker",
        role="mitarbeiter",
        department="Marketing",
    )
    user3.set_password("user123")

    users = [admin, tech1, tech2, user1, user2, user3]
    db.session.add_all(users)
    db.session.flush()

    # ── Tickets erstellen ───────────────────────────
    now = datetime.utcnow()
    tickets_data = [
        {
            "title": "Drucker im 2. OG druckt nicht",
            "description": "Der Netzwerkdrucker HP LaserJet im 2. Obergeschoss reagiert nicht auf Druckaufträge. Die Warteschlange zeigt mehrere ausstehende Aufträge. LED am Drucker blinkt orange.",
            "status": "in_bearbeitung",
            "priority": "hoch",
            "category": "hardware",
            "created_by_id": user1.id,
            "assigned_to_id": tech1.id,
            "created_at": now - timedelta(hours=5),
        },
        {
            "title": "VPN-Verbindung bricht ständig ab",
            "description": "Seit dem letzten Windows-Update kann ich mich nicht stabil mit dem Firmen-VPN verbinden. Die Verbindung trennt sich alle 10-15 Minuten. Betrifft den Cisco AnyConnect Client.",
            "status": "offen",
            "priority": "kritisch",
            "category": "netzwerk",
            "created_by_id": user2.id,
            "assigned_to_id": None,
            "created_at": now - timedelta(hours=2),
        },
        {
            "title": "Neuer Mitarbeiter braucht Zugangsdaten",
            "description": "Ab nächsten Montag fängt ein neuer Kollege in der Marketing-Abteilung an. Benötigt: E-Mail-Konto, Active Directory Account, Zugang zu SharePoint und Teams.",
            "status": "offen",
            "priority": "mittel",
            "category": "zugang",
            "created_by_id": user3.id,
            "assigned_to_id": None,
            "created_at": now - timedelta(hours=8),
        },
        {
            "title": "Outlook stürzt beim Öffnen ab",
            "description": "Microsoft Outlook 365 stürzt sofort nach dem Start ab. Fehlermeldung: 'APPCRASH'. Neustart und Reparatur über Systemsteuerung haben nicht geholfen.",
            "status": "in_bearbeitung",
            "priority": "hoch",
            "category": "software",
            "created_by_id": user1.id,
            "assigned_to_id": tech2.id,
            "created_at": now - timedelta(hours=24),
        },
        {
            "title": "WLAN im Konferenzraum 3 sehr langsam",
            "description": "Das WLAN im Konferenzraum 3 hat seit einer Woche extrem niedrige Geschwindigkeit. Speedtest zeigt nur 2 Mbit/s statt der üblichen 100+ Mbit/s.",
            "status": "wartend",
            "priority": "mittel",
            "category": "netzwerk",
            "created_by_id": user2.id,
            "assigned_to_id": tech1.id,
            "created_at": now - timedelta(days=3),
        },
        {
            "title": "Laptop-Bildschirm flackert",
            "description": "Mein ThinkPad T14 Bildschirm flackert seit gestern unregelmäßig. Besonders bei hellen Hintergründen. Externer Monitor funktioniert normal.",
            "status": "offen",
            "priority": "niedrig",
            "category": "hardware",
            "created_by_id": user3.id,
            "assigned_to_id": None,
            "created_at": now - timedelta(days=1),
        },
        {
            "title": "Passwort zurücksetzen - SAP System",
            "description": "Ich habe mein SAP-Passwort vergessen und bin nach 3 Fehlversuchen gesperrt. Bitte Passwort zurücksetzen.",
            "status": "geschlossen",
            "priority": "mittel",
            "category": "zugang",
            "created_by_id": user2.id,
            "assigned_to_id": tech1.id,
            "created_at": now - timedelta(days=2),
            "closed_at": now - timedelta(days=2, hours=-1),
        },
        {
            "title": "Beamer im Schulungsraum defekt",
            "description": "Der Epson-Beamer im Schulungsraum zeigt kein Bild mehr. Lampe leuchtet rot. Vermutlich muss die Lampe ausgetauscht werden.",
            "status": "geschlossen",
            "priority": "niedrig",
            "category": "hardware",
            "created_by_id": user1.id,
            "assigned_to_id": tech2.id,
            "created_at": now - timedelta(days=5),
            "closed_at": now - timedelta(days=3),
        },
    ]

    tickets = []
    for td in tickets_data:
        ticket = Ticket(**td)
        tickets.append(ticket)
        db.session.add(ticket)

    db.session.flush()

    # ── Kommentare erstellen ────────────────────────
    comments_data = [
        {
            "ticket_id": tickets[0].id,
            "user_id": tech1.id,
            "content": "Habe den Drucker neugestartet und die Warteschlange geleert. Teste gerade ob das Problem weiterhin besteht.",
            "created_at": now - timedelta(hours=3),
        },
        {
            "ticket_id": tickets[0].id,
            "user_id": user1.id,
            "content": "Danke! Nach dem Neustart ging es kurz, aber jetzt hängt er wieder.",
            "created_at": now - timedelta(hours=2),
        },
        {
            "ticket_id": tickets[0].id,
            "user_id": tech1.id,
            "content": "Firmware-Update wird durchgeführt. Drucker ist für ca. 30 Minuten offline.",
            "is_internal": False,
            "created_at": now - timedelta(hours=1),
        },
        {
            "ticket_id": tickets[3].id,
            "user_id": tech2.id,
            "content": "Outlook-Profil wird neu erstellt. Bitte nicht am Rechner arbeiten bis ich fertig bin.",
            "created_at": now - timedelta(hours=20),
        },
        {
            "ticket_id": tickets[4].id,
            "user_id": tech1.id,
            "content": "Access Point wurde überprüft. Warte auf neuen AP von der Bestellung. Voraussichtliche Lieferung: Freitag.",
            "created_at": now - timedelta(days=1),
        },
        {
            "ticket_id": tickets[6].id,
            "user_id": tech1.id,
            "content": "Passwort wurde zurückgesetzt. Neues Einmalpasswort per E-Mail gesendet.",
            "created_at": now - timedelta(days=2, hours=-1),
        },
    ]

    for cd in comments_data:
        comment = Comment(**cd)
        db.session.add(comment)

    db.session.commit()
    print("Demodaten erfolgreich erstellt!")
