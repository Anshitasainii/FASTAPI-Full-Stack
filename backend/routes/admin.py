from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AdminLogin(BaseModel):
    email: str
    password: str

# FIXED ADMIN CREDENTIALS
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

@router.post("/admin-login")
async def admin_login(data: AdminLogin):
    if data.email == ADMIN_EMAIL and data.password == ADMIN_PASSWORD:
        return {"status": "success", "message": "Admin logged in"}
    else:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
