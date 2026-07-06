from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.models.user import User


class AuthService:

    @staticmethod
    def authenticate(
        db: Session,
        email: str,
        password: str,
    ):
        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if not user:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    @staticmethod
    def login(
        db: Session,
        payload,
    ):
        user = AuthService.authenticate(
            db,
            payload.email,
            payload.password,
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        token = create_access_token(
            {
                "sub": str(user.id),
                "role": user.role,
                "email": user.email,
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }