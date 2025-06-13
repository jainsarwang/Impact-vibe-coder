import os
import string
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from passlib.context import CryptContext
from jose import jwt
import logging


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "300"))
ALGORITHM = "HS256"

if not JWT_SECRET_KEY or len(JWT_SECRET_KEY) < 32:
    logging.error("JWT_SECRET_KEY environment variable is not set or is too short. It must be at least 32 characters long.")
    if not JWT_SECRET_KEY:
        logging.warning("JWT_SECRET_KEY not found, generating a temporary one. DO NOT USE THIS IN PRODUCTION.")
        JWT_SECRET_KEY = secrets.token_urlsafe(32)
    elif len(JWT_SECRET_KEY) < 32:
        logging.warning(f"JWT_SECRET_KEY is too short ({len(JWT_SECRET_KEY)} chars), generating a temporary one. DO NOT USE THIS IN PRODUCTION.")
        JWT_SECRET_KEY = secrets.token_urlsafe(32)

# --- Password hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Utility functions ---
def generate_password(length=16) -> str:
    """
    Generate a secure random password with mixed characters.

    Args:
        length (int): Length of the password to generate. Defaults to 16.

    Returns:
        str: A secure random password containing lowercase, uppercase, digits, and special characters.
    """
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password_chars = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%^&*")
    ]
    for _ in range(length - 4):
        password_chars.append(secrets.choice(alphabet))
    secrets.SystemRandom().shuffle(password_chars)
    return ''.join(password_chars)

def generate_username(name: str) -> str:
    """
    Generate a username from a given name.

    Args:
        name (str): Full name to convert into a username.

    Returns:
        str: A username in format 'cleanedname.xyz' where xyz is a random hex.
    """
    base_username = name.lower().replace(" ", "").replace("-", "").replace(".", "")
    base_username = ''.join(c for c in base_username if c.isalnum())
    if not base_username:
        base_username = "user"
    return f"{base_username}.{secrets.token_hex(3)}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to compare against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[timedelta]): Optional custom expiration time.
            If not provided, uses ACCESS_TOKEN_EXPIRE_MINUTES from config.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire.timestamp(), "iat": datetime.now(timezone.utc).timestamp()})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
