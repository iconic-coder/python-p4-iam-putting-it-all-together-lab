"""Minimal local shim for `flask_bcrypt` used by the app and tests.

This provides a very small subset of the real package API so tests can run
without installing the external dependency. It's intentionally simple and
not secure — only suitable for running unit tests in this kata.
"""

class Bcrypt:
    def __init__(self, app=None):
        # real Flask-Bcrypt optionally accepts a Flask app on init
        self.app = app

    def generate_password_hash(self, password):
        # return a bytes-like hash; keep it reversible/simple for tests
        if isinstance(password, str):
            return password.encode('utf-8')
        return password

    def check_password_hash(self, pw_hash, password):
        if isinstance(password, str):
            password = password.encode('utf-8')
        return pw_hash == password
