#!/usr/bin/env python3
"""
HelpDesk Pro - Startskript
Startet den Flask-Server für das IT-Ticketsystem.
"""

import os
import sys
import webbrowser
import threading
from app.main import create_app

HOST = os.environ.get("HELPDESK_HOST", "0.0.0.0")
PORT = int(os.environ.get("HELPDESK_PORT", 5000))
DEBUG = os.environ.get("HELPDESK_DEBUG", "false").lower() == "true"


def open_browser():
    import time
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")


def main():
    print(r"""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║     ██╗  ██╗███████╗██╗     ██████╗              ║
    ║     ██║  ██║██╔════╝██║     ██╔══██╗             ║
    ║     ███████║█████╗  ██║     ██████╔╝             ║
    ║     ██╔══██║██╔══╝  ██║     ██╔═══╝              ║
    ║     ██║  ██║███████╗███████╗██║                   ║
    ║     ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝                   ║
    ║     D E S K   P R O                              ║
    ║                                                  ║
    ║     IT-Support-Ticketsystem v1.0.0               ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    """)
    print(f"  → Dashboard:  http://localhost:{PORT}")
    print(f"  → API:        http://localhost:{PORT}/api/health")
    print(f"  → Demo-Login: admin / admin123")
    print()

    if not DEBUG and "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, daemon=True).start()

    app = create_app()
    app.run(host=HOST, port=PORT, debug=DEBUG)


if __name__ == "__main__":
    main()
