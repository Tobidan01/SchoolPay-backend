from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.core.config import settings
from app.models.user import User
from app.core.security import hash_password

from app.routers import (
    auth,
    class_router,
    fee_structure,
    invoice,
    payment,
    student,
    virtual_account,
    webhook,
)

admin = User(
    first_name="Admin",
    last_name="User",
    email="admin@schoolpay.com",
    password_hash=hash_password("Admin123@"),
    role="ADMIN",
)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(class_router.router)
app.include_router(student.router)
app.include_router(virtual_account.router)
app.include_router(invoice.router)
app.include_router(webhook.router)
app.include_router(fee_structure.router)
app.include_router(payment.router)


@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }