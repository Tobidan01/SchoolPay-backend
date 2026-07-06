from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User


def seed_admin():
    db: Session = SessionLocal()

    try:
        existing = (
            db.query(User)
            .filter(User.email == "admin@schoolpay.com")
            .first()
        )

        if existing:
            print("✅ Admin user already exists.")
            return

        admin = User(
            first_name="Super",
            last_name="Admin",
            email="admin@schoolpay.com",
            password_hash=hash_password("Admin@123"),
            role="ADMIN",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print("🎉 Admin user seeded successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()