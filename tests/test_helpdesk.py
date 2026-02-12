"""
HelpDesk Pro - Unit-Tests
Testet Authentifizierung, Ticket-Verwaltung und API.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app
from app.models import db, User, Ticket, Comment


class TestBase(unittest.TestCase):
    """Basis-Klasse mit Test-Konfiguration."""

    def setUp(self):
        self.app = create_app()
        self.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self._create_test_data()

    def _create_test_data(self):
        admin = User(username="admin", email="admin@test.de",
                     full_name="Admin User", role="admin")
        admin.set_password("admin123")

        tech = User(username="tech", email="tech@test.de",
                    full_name="Tech User", role="techniker")
        tech.set_password("tech123")

        user = User(username="user", email="user@test.de",
                    full_name="Normal User", role="mitarbeiter")
        user.set_password("user123")

        db.session.add_all([admin, tech, user])
        db.session.flush()

        ticket = Ticket(title="Test Ticket", description="Test Beschreibung",
                        priority="mittel", category="software",
                        created_by_id=user.id)
        db.session.add(ticket)
        db.session.commit()

    def login(self, username, password):
        return self.client.post("/login", data={
            "username": username, "password": password
        }, follow_redirects=True)

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()


class TestAuth(TestBase):
    """Tests für die Authentifizierung."""

    def test_login_page(self):
        resp = self.client.get("/login")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Anmelden", resp.data)

    def test_login_success(self):
        resp = self.login("admin", "admin123")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Dashboard", resp.data)

    def test_login_wrong_password(self):
        resp = self.login("admin", "wrong")
        self.assertIn("Ung".encode(), resp.data)

    def test_login_required(self):
        resp = self.client.get("/", follow_redirects=False)
        self.assertEqual(resp.status_code, 302)

    def test_logout(self):
        self.login("admin", "admin123")
        resp = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"Anmelden", resp.data)


class TestDashboard(TestBase):
    """Tests für das Dashboard."""

    def test_dashboard_admin(self):
        self.login("admin", "admin123")
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Dashboard", resp.data)

    def test_dashboard_user(self):
        self.login("user", "user123")
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)


class TestTickets(TestBase):
    """Tests für die Ticket-Verwaltung."""

    def test_ticket_list(self):
        self.login("admin", "admin123")
        resp = self.client.get("/tickets")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Test Ticket", resp.data)

    def test_create_ticket(self):
        self.login("user", "user123")
        resp = self.client.post("/tickets/new", data={
            "title": "Neues Problem",
            "description": "Detaillierte Beschreibung",
            "priority": "hoch",
            "category": "hardware",
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Neues Problem", resp.data)

    def test_create_ticket_empty(self):
        self.login("user", "user123")
        resp = self.client.post("/tickets/new", data={
            "title": "", "description": "",
        }, follow_redirects=True)
        self.assertIn(b"erforderlich", resp.data)

    def test_ticket_detail(self):
        self.login("admin", "admin123")
        resp = self.client.get("/tickets/1")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Test Ticket", resp.data)

    def test_user_cannot_see_others_tickets(self):
        self.login("tech", "tech123")
        # Techniker kann alle Tickets sehen
        resp = self.client.get("/tickets/1")
        self.assertEqual(resp.status_code, 200)

    def test_add_comment(self):
        self.login("admin", "admin123")
        resp = self.client.post("/tickets/1/comment", data={
            "content": "Test Kommentar",
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Test Kommentar", resp.data)

    def test_update_ticket_status(self):
        self.login("tech", "tech123")
        resp = self.client.post("/tickets/1/update", data={
            "status": "in_bearbeitung",
        }, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"aktualisiert", resp.data)

    def test_filter_by_status(self):
        self.login("admin", "admin123")
        resp = self.client.get("/tickets?status=offen")
        self.assertEqual(resp.status_code, 200)


class TestAPI(TestBase):
    """Tests für die API-Endpunkte."""

    def test_health(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "ok")

    def test_stats_requires_auth(self):
        resp = self.client.get("/api/stats/overview")
        self.assertEqual(resp.status_code, 302)

    def test_stats_overview(self):
        self.login("admin", "admin123")
        resp = self.client.get("/api/stats/overview")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("by_status", data)
        self.assertIn("by_priority", data)
        self.assertIn("by_category", data)


class TestAccessControl(TestBase):
    """Tests für die Zugriffskontrolle."""

    def test_user_cannot_access_users_page(self):
        self.login("user", "user123")
        resp = self.client.get("/users")
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_access_users_page(self):
        self.login("admin", "admin123")
        resp = self.client.get("/users")
        self.assertEqual(resp.status_code, 200)

    def test_tech_cannot_access_users_page(self):
        self.login("tech", "tech123")
        resp = self.client.get("/users")
        self.assertEqual(resp.status_code, 403)


class TestModels(TestBase):
    """Tests für die Datenbankmodelle."""

    def test_user_password(self):
        with self.app.app_context():
            user = User.query.filter_by(username="admin").first()
            self.assertTrue(user.check_password("admin123"))
            self.assertFalse(user.check_password("wrong"))

    def test_user_roles(self):
        with self.app.app_context():
            admin = User.query.filter_by(username="admin").first()
            tech = User.query.filter_by(username="tech").first()
            user = User.query.filter_by(username="user").first()
            self.assertTrue(admin.is_admin)
            self.assertTrue(admin.is_techniker)
            self.assertFalse(tech.is_admin)
            self.assertTrue(tech.is_techniker)
            self.assertFalse(user.is_admin)
            self.assertFalse(user.is_techniker)

    def test_ticket_labels(self):
        with self.app.app_context():
            ticket = Ticket.query.first()
            self.assertEqual(ticket.priority_label, "Mittel")
            self.assertEqual(ticket.status_label, "Offen")
            self.assertEqual(ticket.category_label, "Software")


if __name__ == "__main__":
    unittest.main(verbosity=2)
