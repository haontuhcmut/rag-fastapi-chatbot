import logging
import uuid
import jwt

from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext
from datetime import timedelta, timezone, datetime
from fastapi.security import OAuth2PasswordBearer

from app.config import Config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="token")

serialize = URLSafeSerializer(
    secret_key=Config.SECRET_KEY,
    salt=Config.SALT,
)


def encode_url_safe_token(data: dict):
    token = serialize.dumps(data)
    return token


def get_hashed_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def decode_url_safe_token(token: str):
    try:
        token_data = serialize.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))


def create_access_token(
    user_data: dict, expire_delta: timedelta | None = None, refresh: bool | None = False
):
    payload = {"user": user_data}
    if expire_delta:
        expire = datetime.now(timezone.utc) + expire_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload.update({"exp": expire, "jti": str(uuid.uuid4()), "refresh": refresh})
    token = jwt.encode(
        payload=payload, key=Config.SECRET_KEY, algorithm=Config.ALGORITHM
    )
    return token

