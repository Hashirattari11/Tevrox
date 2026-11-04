import argparse

from sqlalchemy import select

from app.core.security import hash_password
from app.database.models import User, UserRole
from app.database.session import SessionLocal

parser = argparse.ArgumentParser()
parser.add_argument("email")
parser.add_argument("password")
args = parser.parse_args()
email = args.email.strip().lower()

with SessionLocal() as db:
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, password_hash=hash_password(args.password), role=UserRole.admin)
        db.add(user)
    else:
        user.role = UserRole.admin
    db.commit()

print("Admin user created or promoted.")
