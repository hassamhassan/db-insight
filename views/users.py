from datetime import datetime, timedelta
from typing import Dict

from config import (
    JWT_SECRET,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE
)
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from jose import jwt, JOSEError
from passlib.context import CryptContext

from database.db import get_db
from models.user import User, UserMethods

HASH_STRING = CryptContext(schemes=["bcrypt"])


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the provided plain password matches the hashed password.

    Args:
        plain_password: str - The plain text password.
        hashed_password: str - The hashed password to be verified against.

    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return HASH_STRING.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """
    Hash the provided password.

    Args:
        password: str - The password to be hashed.

    Returns:
        str: The hashed password.
    """
    return HASH_STRING.hash(password)


async def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user by verifying the provided email and password.

    Args:
        db: Database Session.
        email: str - The user's email.
        password: str - The user's password.

    Returns:
        User - The authenticated user object.
    """
    user = UserMethods.get_record_with_(db, email=email)
    if user and verify_password_hash(password, user.password):
        return user


async def create_access_token(data: dict) -> str:
    """
    Create an access token based on the provided data.

    Args:
        data: dict - The data to encode into the token.

    Returns:
        str: The generated access token.
    """
    data["type"] = "access_token"
    data["exp"] = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE))
    data["iat"] = datetime.utcnow()
    return jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)


async def verify_user(
        db: Session = Depends(get_db),
        authentication: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> User:
    """
    Verify the user based on the provided authentication credentials.

    Args:
        db: Database Session.
        authentication: HTTPAuthorizationCredentials - The user authentication credentials.

    Returns:
        User: Authenticated User's object.
    """
    authentication_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload: Dict = jwt.decode(
            authentication.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
    except JOSEError:
        raise authentication_error

    user = UserMethods.get_record_with_(db, email=payload.get("email"))
    if not user:
        raise authentication_error

    return user
