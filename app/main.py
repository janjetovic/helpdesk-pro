"""
HelpDesk Pro - Hauptanwendung
Flask-Server mit Authentifizierung, Ticket-Verwaltung und Dashboard.
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for, request,
    flash, jsonify, abort
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)

from app.models import db, User, Ticket, Comment
from app.seed import seed_database


def techniker_required(f):
    """Dekorator: Erfordert Techniker- oder Admin-Rolle."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_techniker:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Dekorator: Erfordert Admin-Rolle."""
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def create_app():
    """Flask-Anwendung erstellen und konfigurieren."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "helpdesk-dev-key-change-in-prod")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'helpdesk.db')}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Erweiterungen initialisieren
    db.init_app(app)
    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Bitte melden Sie sich an."

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Datenbank und Demodaten erstellen
    with app.app_context():
        db.create_all()
        seed_database()

    # ── Authentifizierung ────────────────────────────

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))

        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            else:
                flash("Ungültiger Benutzername oder Passwort.", "error")

        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    # ── Dashboard ────────────────────────────────────

    @app.route("/")
    @login_required
    def dashboard():
        # Statistiken berechnen
        if current_user.is_techniker:
            tickets = Ticket.query
        else:
            tickets = Ticket.query.filter_by(created_by_id=current_user.id)

        total = tickets.count()
        offen = tickets.filter_by(status="offen").count()
        in_bearbeitung = tickets.filter_by(status="in_bearbeitung").count()
        wartend = tickets.filter_by(status="wartend").count()
        geschlossen = tickets.filter_by(status="geschlossen").count()

        # Tiketi po prioritetu
        kritisch = tickets.filter_by(priority="kritisch").filter(Ticket.status != "geschlossen").count()
        hoch = tickets.filter_by(priority="hoch").filter(Ticket.status != "geschlossen").count()

        # Tiketi po kategoriji
        categories = {}
        for cat in Ticket.CATEGORIES:
            categories[cat] = tickets.filter_by(category=cat).count()

        # Poslednji tiketi
        if current_user.is_techniker:
            recent = Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()
            my_assigned = Ticket.query.filter_by(
                assigned_to_id=current_user.id
            ).filter(Ticket.status != "geschlossen").order_by(Ticket.priority.desc()).all()
        else:
            recent = Ticket.query.filter_by(
                created_by_id=current_user.id
            ).order_by(Ticket.created_at.desc()).limit(5).all()
            my_assigned = []

        stats = {
            "total": total,
            "offen": offen,
            "in_bearbeitung": in_bearbeitung,
            "wartend": wartend,
            "geschlossen": geschlossen,
            "kritisch": kritisch,
            "hoch": hoch,
            "categories": categories,
        }

        return render_template(
            "dashboard.html",
            stats=stats,
            recent_tickets=recent,
            my_assigned=my_assigned,
        )

    # ── Ticket-Verwaltung ────────────────────────────

    @app.route("/tickets")
    @login_required
    def ticket_list():
        status_filter = request.args.get("status", "alle")
        priority_filter = request.args.get("priority", "alle")
        category_filter = request.args.get("category", "alle")
        search = request.args.get("q", "").strip()

        query = Ticket.query

        # Mitarbeiter sehen nur eigene Tickets
        if not current_user.is_techniker:
            query = query.filter_by(created_by_id=current_user.id)

        if status_filter != "alle":
            query = query.filter_by(status=status_filter)
        if priority_filter != "alle":
            query = query.filter_by(priority=priority_filter)
        if category_filter != "alle":
            query = query.filter_by(category=category_filter)
        if search:
            query = query.filter(
                Ticket.title.ilike(f"%{search}%") | Ticket.description.ilike(f"%{search}%")
            )

        tickets = query.order_by(Ticket.created_at.desc()).all()

        return render_template(
            "tickets.html",
            tickets=tickets,
            status_filter=status_filter,
            priority_filter=priority_filter,
            category_filter=category_filter,
            search=search,
        )

    @app.route("/tickets/new", methods=["GET", "POST"])
    @login_required
    def ticket_new():
        if request.method == "POST":
            title = request.form.get("title", "").strip()
            description = request.form.get("description", "").strip()
            priority = request.form.get("priority", "mittel")
            category = request.form.get("category", "software")

            if not title or not description:
                flash("Titel und Beschreibung sind erforderlich.", "error")
                return render_template("ticket_form.html", edit=False)

            ticket = Ticket(
                title=title,
                description=description,
                priority=priority,
                category=category,
                created_by_id=current_user.id,
            )
            db.session.add(ticket)
            db.session.commit()

            flash(f"Ticket #{ticket.id} wurde erstellt.", "success")
            return redirect(url_for("ticket_detail", ticket_id=ticket.id))

        return render_template("ticket_form.html", edit=False)

    @app.route("/tickets/<int:ticket_id>")
    @login_required
    def ticket_detail(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)

        # Zugriffskontrolle
        if not current_user.is_techniker and ticket.created_by_id != current_user.id:
            abort(403)

        technikers = User.query.filter(User.role.in_(["admin", "techniker"])).all()

        return render_template(
            "ticket_detail.html",
            ticket=ticket,
            technikers=technikers,
        )

    @app.route("/tickets/<int:ticket_id>/update", methods=["POST"])
    @login_required
    def ticket_update(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)

        if not current_user.is_techniker and ticket.created_by_id != current_user.id:
            abort(403)

        # Status ändern (nur Techniker)
        new_status = request.form.get("status")
        if new_status and current_user.is_techniker and new_status in Ticket.STATUSES:
            old_status = ticket.status
            ticket.status = new_status
            if new_status == "geschlossen" and not ticket.closed_at:
                ticket.closed_at = datetime.utcnow()
            elif new_status != "geschlossen":
                ticket.closed_at = None

        # Zuweisung ändern (nur Techniker)
        assigned_to = request.form.get("assigned_to_id")
        if assigned_to is not None and current_user.is_techniker:
            ticket.assigned_to_id = int(assigned_to) if assigned_to else None

        # Priorität ändern (nur Techniker)
        new_priority = request.form.get("priority")
        if new_priority and current_user.is_techniker and new_priority in Ticket.PRIORITIES:
            ticket.priority = new_priority

        ticket.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Ticket wurde aktualisiert.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket.id))

    @app.route("/tickets/<int:ticket_id>/comment", methods=["POST"])
    @login_required
    def ticket_comment(ticket_id):
        ticket = Ticket.query.get_or_404(ticket_id)

        if not current_user.is_techniker and ticket.created_by_id != current_user.id:
            abort(403)

        content = request.form.get("content", "").strip()
        is_internal = request.form.get("is_internal") == "on"

        if not content:
            flash("Kommentar darf nicht leer sein.", "error")
            return redirect(url_for("ticket_detail", ticket_id=ticket.id))

        comment = Comment(
            content=content,
            is_internal=is_internal and current_user.is_techniker,
            ticket_id=ticket.id,
            user_id=current_user.id,
        )
        db.session.add(comment)
        ticket.updated_at = datetime.utcnow()
        db.session.commit()

        flash("Kommentar hinzugefügt.", "success")
        return redirect(url_for("ticket_detail", ticket_id=ticket.id))

    # ── Benutzerverwaltung (nur Admin) ───────────────

    @app.route("/users")
    @admin_required
    def user_list():
        users = User.query.order_by(User.role, User.full_name).all()
        return render_template("users.html", users=users)

    # ── API-Endpunkte für Dashboard-Diagramme ────────

    @app.route("/api/stats/overview")
    @login_required
    def api_stats_overview():
        if current_user.is_techniker:
            base = Ticket.query
        else:
            base = Ticket.query.filter_by(created_by_id=current_user.id)

        return jsonify({
            "by_status": {
                "offen": base.filter_by(status="offen").count(),
                "in_bearbeitung": base.filter_by(status="in_bearbeitung").count(),
                "wartend": base.filter_by(status="wartend").count(),
                "geschlossen": base.filter_by(status="geschlossen").count(),
            },
            "by_priority": {
                "niedrig": base.filter(Ticket.status != "geschlossen").filter_by(priority="niedrig").count(),
                "mittel": base.filter(Ticket.status != "geschlossen").filter_by(priority="mittel").count(),
                "hoch": base.filter(Ticket.status != "geschlossen").filter_by(priority="hoch").count(),
                "kritisch": base.filter(Ticket.status != "geschlossen").filter_by(priority="kritisch").count(),
            },
            "by_category": {
                cat: base.filter_by(category=cat).count() for cat in Ticket.CATEGORIES
            },
        })

    @app.route("/api/health")
    def api_health():
        return jsonify({"status": "ok", "service": "HelpDesk Pro", "version": "1.0.0"})

    # ── Fehlerbehandlung ─────────────────────────────

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message="Zugriff verweigert"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Seite nicht gefunden"), 404

    # ── Template-Filter ──────────────────────────────

    @app.template_filter("timeago")
    def timeago_filter(dt):
        if not dt:
            return "–"
        diff = datetime.utcnow() - dt
        secs = diff.total_seconds()
        if secs < 60:
            return "gerade eben"
        if secs < 3600:
            return f"vor {int(secs // 60)} Min"
        if secs < 86400:
            return f"vor {int(secs // 3600)} Std"
        return f"vor {int(secs // 86400)} Tagen"

    @app.template_filter("datetime_format")
    def datetime_format(dt, fmt="%d.%m.%Y %H:%M"):
        if not dt:
            return "–"
        return dt.strftime(fmt)

    return app
