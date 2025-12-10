from pydantic import BaseModel
from datetime import date
from typing import Optional

class UserCreate(BaseModel):
   name: str
   email: str
   password: str
   first_name: Optional[str] = None
   last_name: Optional[str] = None
   dob: Optional[date] = None
   mobile: Optional[str] = None
   professional_summary: Optional[str] = None
   gender: Optional[str] = None
   job_status: Optional[str] = None

class UserUpdate(BaseModel):
   name: Optional[str] = None
   email: Optional[str] = None
   password: Optional[str] = None
   first_name: Optional[str] = None
   last_name: Optional[str] = None
   dob: Optional[date] = None
   mobile: Optional[str] = None
   professional_summary: Optional[str] = None
   gender: Optional[str] = None
   job_status: Optional[str] = None

class User(UserCreate):
   id: int

class Login(BaseModel):
   email: str
   password: str   