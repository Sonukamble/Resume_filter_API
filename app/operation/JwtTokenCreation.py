from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

SECRET_KEY = "197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTE = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTE)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_password_reset_token(email: str):
    token_data = {
        "sub": email,
        "exp": datetime.utcnow() + timedelta(minutes=30)  # 30 minutes expiration
    }
    reset_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return reset_token


def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")  # Return the email if valid
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid reset token")
