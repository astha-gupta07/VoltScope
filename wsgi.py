"""
VoltScope — WSGI Entry Point
Standard production gateway for Gunicorn (Linux/Cloud) and Waitress (Windows).
"""

from app import app

if __name__ == "__main__":
    app.run()
