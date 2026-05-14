from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "aquality_secret"
ALGORITHM = "HS256"


def crear_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(hours=8)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)