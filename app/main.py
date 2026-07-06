from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

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

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
)

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