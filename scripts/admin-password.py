"""Run using backend/.venv/bin/python. Does not store the cleartext password."""
from getpass import getpass
from argon2 import PasswordHasher
password = getpass("New admin password (16+ characters): ")
if len(password) < 16:
    raise SystemExit("Use at least 16 characters")
if password != getpass("Repeat: "):
    raise SystemExit("Passwords do not match")
print("ADMIN_PASSWORD_HASH='" + PasswordHasher().hash(password) + "'")
