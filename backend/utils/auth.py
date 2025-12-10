from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from datetime import datetime
from utils.jwt import SECRET_KEY, ALGORITHM
from config.db import conn
from models.index import users
from sqlalchemy import select

# Dependency to verify token
def get_current_user(token: str):
    try:
        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: no user id",
            )

        # Query DB for user
        query = select(users).where(users.c.id == user_id)
        result = conn.execute(query).fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return dict(result._mapping)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
