"""
HelpDesk Pro - Datenbankmodelle
Definiert Benutzer, Tickets und Kommentare mit SQLAlchemy ORM.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Benutzer mit Rollen: admin, techniker, mitarbeiter."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="mitarbeiter")
    department = db.Column(db.String(80), default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Beziehungen
    tickets_created = db.relationship(
        "Ticket", foreign_keys="Ticket.created_by_id", backref="creator", lazy=True
    )
    tickets_assigned = db.relationship(
        "Ticket", foreign_keys="Ticket.assigned_to_id", backref="assignee", lazy=True
    )
    comments = db.relationship("Comment", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def is_techniker(self):
        return self.role in ("admin", "techniker")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Ticket(db.Model):
    """Support-Ticket mit Status, Priorität und Kategorie."""
    __tablename__ = "tickets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="offen")
    priority = db.Column(db.String(20), nullable=False, default="mittel")
    category = db.Column(db.String(50), nullable=False, default="software")

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime, nullable=True)

    # Beziehungen
    comments = db.relationship(
        "Comment", backref="ticket", lazy=True, order_by="Comment.created_at"
    )

    STATUSES = ["offen", "in_bearbeitung", "wartend", "geschlossen"]
    PRIORITIES = ["niedrig", "mittel", "hoch", "kritisch"]
    CATEGORIES = ["hardware", "software", "netzwerk", "zugang", "sonstiges"]

    PRIORITY_LABELS = {
        "niedrig": "Niedrig",
        "mittel": "Mittel",
        "hoch": "Hoch",
        "kritisch": "Kritisch",
    }

    STATUS_LABELS = {
        "offen": "Offen",
        "in_bearbeitung": "In Bearbeitung",
        "wartend": "Wartend",
        "geschlossen": "Geschlossen",
    }

    CATEGORY_LABELS = {
        "hardware": "Hardware",
        "software": "Software",
        "netzwerk": "Netzwerk",
        "zugang": "Zugang / Berechtigungen",
        "sonstiges": "Sonstiges",
    }

    @property
    def priority_label(self):
        return self.PRIORITY_LABELS.get(self.priority, self.priority)

    @property
    def status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)

    @property
    def category_label(self):
        return self.CATEGORY_LABELS.get(self.category, self.category)

    @property
    def age_hours(self):
        delta = datetime.utcnow() - self.created_at
        return round(delta.total_seconds() / 3600, 1)

    def __repr__(self):
        return f"<Ticket #{self.id}: {self.title}>"


class Comment(db.Model):
    """Kommentar zu einem Ticket."""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)

    ticket_id = db.Column(db.Integer, db.ForeignKey("tickets.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Comment #{self.id} on Ticket #{self.ticket_id}>"
