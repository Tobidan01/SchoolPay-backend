from fastapi import FastAPI

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
    title="SchoolPay API",
    version="1.0.0",
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
def health_check():
    return {
        "message": "SchoolPay API is running"
    }