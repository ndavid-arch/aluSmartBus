"""Create a user account from the terminal, for testing and for the first administrator.

Run from the backend folder, for example:
    python -m app.create_user --name "Test Student" --email student@alustudent.com --role student
"""

import argparse
import getpass

from sqlalchemy import select

from app.core.security import MIN_PASSWORD_LENGTH, hash_password
from app.db import SessionLocal
from app.models import Role, User


def parse_args() -> argparse.Namespace:
    """Read the name, email and role from the command line."""
    parser = argparse.ArgumentParser(description="Create a SmartBus user.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--role", required=True, choices=[role.value for role in Role])
    return parser.parse_args()


def ask_password() -> str:
    """Ask for the password twice without showing it, so it never appears in the history."""
    password = getpass.getpass("Password: ")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    if getpass.getpass("Repeat password: ") != password:
        raise SystemExit("The passwords do not match.")
    return password


def main() -> None:
    """Create the user unless the email is already taken."""
    args = parse_args()
    email = args.email.strip().lower()
    with SessionLocal() as session:
        if session.scalar(select(User).where(User.email == email)) is not None:
            raise SystemExit(f"A user with the email {email} already exists.")
        user = User(
            full_name=args.name,
            email=email,
            password_hash=hash_password(ask_password()),
            role=Role(args.role),
        )
        session.add(user)
        session.commit()
        print(f"Created {user.role.value} {user.full_name} ({user.email}).")


if __name__ == "__main__":
    main()
