from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "SUPER_SECRET_KEY_PLEASE_CHANGE_THIS"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token
