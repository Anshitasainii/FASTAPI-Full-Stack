
from fastapi import APIRouter, Depends
from utils.hash import verify_password, hash_password
from utils.jwt import create_access_token, SECRET_KEY, ALGORITHM
from config.db import conn
from models.index import users
from sqlalchemy import select,and_
from schemas.index import User, UserCreate, UserUpdate, Login
from jose import jwt, JWTError
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from datetime import datetime, timedelta
from secrets import randbelow
from decouple import config  #
import os
from pathlib import Path
from fastapi import File, UploadFile, Form

router = APIRouter()
UPLOAD_DIR = "uploads/profile_images"
Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


# Email configuration
mail_conf = ConnectionConfig(
    MAIL_USERNAME=config("MAIL_USERNAME"),
    MAIL_PASSWORD=config("MAIL_PASSWORD"),
    MAIL_FROM=config("MAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

# ============================================================
# 1️⃣ READ ALL (Static route MUST be at top)
# ============================================================
@router.get("/all")
async def read_all():
    try:
        result = conn.execute(users.select()).fetchall()
        users_list = []
        for row in result:
            user_dict = dict(row._mapping)
            # Handle missing columns gracefully
            if 'professional_summary' not in user_dict:
                user_dict['professional_summary'] = None
            if 'gender' not in user_dict:
                user_dict['gender'] = None
            if 'job_status' not in user_dict:
                user_dict['job_status'] = None
            users_list.append(user_dict)
        return users_list
    except Exception as e:
        print(f"Error in /all endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Database error: {str(e)}"}

# @user.get("/test-mail")
# async def test_mail():
#     message = MessageSchema(
#         subject="Test Email",
#         recipients=["anshitasaini30@gmail.com"],
#         body="<h1>Working! </h1>",
#         subtype="html"
#     )

#     fm = FastMail(mail_conf)
#     await fm.send_message(message)

#     return {"message": "Email sent!"}

#  LOGIN 
@router.post("/login")
def login(data: Login):
    print("LOGIN PASSWORD RECEIVED:", data.password)
    print("LOGIN TYPE:", type(data.password))

    email = data.email
    password = data.password

    query = select(users).where(users.c.email == email)
    result = conn.execute(query).fetchone()

    if not result:
        return {"error": "Invalid email"}

    user_data = dict(result._mapping)

    if not verify_password(password, user_data["password"]):
        return {"error": "Invalid password"}

    token = create_access_token({"id": user_data["id"]})
    return {"message": "Login successful", "token": token}

# PROFILE 
@router.get("/profile")
def get_profile(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")

        query = select(users).where(users.c.id == user_id)
        result = conn.execute(query).fetchone()

        if not result:
            return {"error": "User not found"}

        user_data = dict(result._mapping)

        # ⭐ ADD THIS — Build full image URL
        if user_data.get("profile_image"):
            ts=datetime.now().timestamp()
            user_data["profile_image_url"] = (
                f"http://127.0.0.1:8000/uploads/profile_images/{user_data['profile_image']}?v={ts}"
            )
        else:
            user_data["profile_image_url"] = None

        return user_data

    except JWTError:
        return {"error": "Invalid or expired token"}


#  CREATE USER 

@router.post("/register")
async def create_user(data: UserCreate):

    print("---- REGISTER API CALLED ----")
    print("Incoming:", data)

    if not data.name or not data.email or not data.password:
        print("Missing fields")
        return {"error": "All fields are required"}

    existing = conn.execute(
        select(users).where(users.c.email == data.email)
    ).fetchone()

    print("Existing user:", existing)

    if existing:
        print("Duplicate found!")
        return {"error": "Duplicate email not allowed"}

    otp = str(randbelow(900000) + 100000)
    expiry = datetime.now() + timedelta(minutes=10)
    hashed_pwd = hash_password(data.password)

    try:
        result = conn.execute(
            users.insert().values(
                name=data.name,
                email=data.email,
                password=hashed_pwd,
                otp=otp,
                otp_expiry=expiry,
                verified=False
            )
        )
        conn.commit()
        print("User inserted with ID:", result.lastrowid)

    except Exception as e:
        print("DB INSERT ERROR:", e)
        return {"error": "DB insert failed", "details": str(e)}

    # EMAIL SENDING
    try:
        print("Sending OTP email...")
        message = MessageSchema(
            subject="Verification Code",
            recipients=[data.email],
            body=f"Your OTP is {otp}",
            subtype="plain"
        )
        fm = FastMail(mail_conf)
        await fm.send_message(message)
        print("Email sent!")

    except Exception as e:
        print("EMAIL ERROR:", e)
        
        # ROLLBACK user because email failed
        conn.execute(users.delete().where(users.c.id == result.lastrowid))
        conn.commit()
        
        return {"error": "Email failed", "details": str(e)}

    return {"message": "OTP sent", "user_id": result.lastrowid}

@router.post("/verify")
async def verify_account(user_id: int, otp: str):

    query = select(users).where(users.c.id == user_id)
    result = conn.execute(query).fetchone()

    if not result:
        return {"error": "User not found"}

    user_data = dict(result._mapping)

    if user_data["verified"]:
        return {"message": "Already verified"}

    if user_data["otp"] != otp:
        return {"error": "Invalid OTP"}

    if datetime.now() > user_data["otp_expiry"]:
        return {"error": "OTP expired"}

    conn.execute(
        users.update()
        .where(users.c.id == user_id)
        .values(verified=True, otp=None, otp_expiry=None)
    )
    conn.commit()

    return {"message": "Account verified successfully"}
@router.post("/google-login")
async def google_login(payload: dict):
    email = payload.get("email")
    name = payload.get("name")

    if not email:
        return {"error": "Email missing from Google login"}

    # 1️⃣ Check if user already exists
    query = select(users).where(users.c.email == email)
    existing_user = conn.execute(query).fetchone()

    # 2️⃣ If user exists → just return token
    if existing_user:
        token = create_access_token({"id": existing_user.id})
        return {"token": token, "message": "Login successful"}

    # 3️⃣ If first time → auto-create account
    result = conn.execute(
        users.insert().values(
            name=name,
            email=email,
            password="",      # No password since Google login
            verified=True,
            otp=None,
            otp_expiry=None,
            profile_image=None
        )
    )
    conn.commit()

    user_id = result.lastrowid

    token = create_access_token({"id": user_id})
    return {
        "token": token,
        "message": "Account created with Google",
        "user_id": user_id
    }

@router.post("/upload-profile")
async def upload_profile(
    user_id: int = Form(...),
    file: UploadFile = File(...)
):

    # Validate file
    allowed = ["jpg", "jpeg", "png"]
    ext = file.filename.split(".")[-1].lower()

    if ext not in allowed:
        return {"error": "Invalid image format (allowed: jpg, jpeg, png)"}

    # Create filename
    filename = f"user_{user_id}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Save file
    with open(filepath, "wb") as buffer:
        buffer.write(await file.read())

    # Save filename in DB
    conn.execute(
        users.update()
        .where(users.c.id == user_id)
        .values(profile_image=filename)
    )
    conn.commit()

    return {
        "message": "Profile image uploaded successfully!",
        "filename": filename,
        "url": f"http://127.0.0.1:8000/uploads/profile_images/{filename}?v={datetime.now().timestamp()}"
    }

# ============================================================
# 5️⃣ READ ONE (Dynamic Route)
# ============================================================
@router.get("/{id}")
async def read_one(id: int):
    try:
        result = conn.execute(users.select().where(users.c.id == id)).fetchone()
        if not result:
            return {"error": "Not Found"}
        user_dict = dict(result._mapping)
        # Handle missing columns gracefully
        if 'professional_summary' not in user_dict:
            user_dict['professional_summary'] = None
        if 'gender' not in user_dict:
            user_dict['gender'] = None
        if 'job_status' not in user_dict:
            user_dict['job_status'] = None
        return user_dict
    except Exception as e:
        print(f"Error in /{id} endpoint: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Database error: {str(e)}"}

# ============================================================
# 6️⃣ UPDATE USER (with full validation + debug logs)
# ============================================================
@router.put("/{id}")
async def update_user(id: int, data: UserUpdate):
    print("---- UPDATE CALLED ----")
    print("Incoming id:", id)
    print("Incoming data:", data)

    # 1) Fetch existing user
    existing_q = select(users).where(users.c.id == id)
    old_user = conn.execute(existing_q).fetchone()
    print("Old user:", old_user)

    if not old_user:
        print("User not found in DB")
        return {"error": "User not found"}

    # 2) Prepare update values
    update_values = {}
    
    # Name and email (required if provided)
    if data.name is not None:
        name = data.name.strip() if data.name else ""
        if not name:
            return {"error": "Name cannot be empty"}
        update_values["name"] = name
    
    if data.email is not None:
        email = data.email.lower().strip() if data.email else ""
        if not email:
            return {"error": "Email cannot be empty"}
        
        # Check if email is used by another user
        email_q = select(users).where(
            and_(
                users.c.email == email,
                users.c.id != id
            )
        )
        email_exists = conn.execute(email_q).fetchone()
        if email_exists:
            return {"error": "Duplicate email not allowed"}
        update_values["email"] = email

    # Password: keep old if not provided
    if data.password is not None and data.password.strip():
        update_values["password"] = hash_password(data.password)
    elif data.password is None:
        # Keep old password
        pass

    # New fields
    if data.first_name is not None:
        update_values["first_name"] = data.first_name.strip() if data.first_name else None
    if data.last_name is not None:
        update_values["last_name"] = data.last_name.strip() if data.last_name else None
    if data.dob is not None:
        update_values["dob"] = data.dob
    if data.mobile is not None:
        update_values["mobile"] = data.mobile.strip() if data.mobile else None
    if data.professional_summary is not None:
        update_values["professional_summary"] = data.professional_summary.strip() if data.professional_summary else None
    if data.gender is not None:
        update_values["gender"] = data.gender.strip() if data.gender else None
    if data.job_status is not None:
        update_values["job_status"] = data.job_status.strip() if data.job_status else None

    # 3) Perform update
    if update_values:
        update_q = users.update().where(users.c.id == id).values(**update_values)
        result = conn.execute(update_q)
        conn.commit()
        print("Rows updated:", result.rowcount)
        print("---- UPDATE DONE ----")
        return {"success": True, "message": "User Updated Successfully"}
    else:
        return {"error": "No fields to update"}

# ============================================================
# 7️⃣ DELETE USER
# ============================================================
@router.delete("/{id}")
async def delete_user(id: int):

    # check user exists
    existing_user = conn.execute(select(users).where(users.c.id == id)).fetchone()
    if not existing_user:
        return {"error": "User does not exist"}

    conn.execute(users.delete().where(users.c.id == id))
    conn.commit()

    return {"success": True, "message": "User Deleted"}
