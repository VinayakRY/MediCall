import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext

load_dotenv()

SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "CHANGE_THIS_SECRET_BEFORE_DEPLOYMENT",
)

ALGORITHM = "HS256"

ACCESS_TOKEN_MINUTES = int(
    os.getenv("ACCESS_TOKEN_MINUTES", "480")
)

# IMPORTANT:
# Do NOT use bcrypt here.
# PBKDF2-SHA256 does not have bcrypt's 72-byte limitation.
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("Password must be a string.")

    if not password:
        raise ValueError("Password cannot be empty.")

    return pwd_context.hash(password)


def verify_password(
    password: str,
    password_hash: str,
) -> bool:

    if not password or not password_hash:
        return False

    try:
        return pwd_context.verify(
            password,
            password_hash,
        )
    except Exception:
        return False


def create_access_token(user_id: int) -> str:

    expires = (
        datetime.now(timezone.utc)
        + timedelta(minutes=ACCESS_TOKEN_MINUTES)
    )

    payload = {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def decode_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        return int(payload["sub"])

    except (
        JWTError,
        KeyError,
        ValueError,
        TypeError,
    ):

        return None