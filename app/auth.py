"""Authentication module."""
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password):
    """Get a password hash."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    """Verify a password."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create an access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
