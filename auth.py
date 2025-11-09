from passlib.context import CryptContext
import datetime as dt
import jwt
import secrets
import os
import dotenv

from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException, status

from entities import Token, TokenData

dotenv.load_dotenv()

# Секретний ключ для JWT
# Рекомендовано використовувати змінну середовища у реальних додатках
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"

# Зміна алгоритму хешування на sha256_crypt для кращої сумісності з passlib
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Хешування пароля
def hash_password(password: str) -> str:
    """Хешує наданий пароль."""
    # sha256_crypt не має ліміту 72 байти, як bcrypt
    return pwd_context.hash(password)

# Перевірка пароля
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Перевіряє відповідність пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)

# Створення JWT токена
def create_access_token(user_id: int, minutes: int = 30) -> str:
    """Створює токен доступу JWT із ID користувача та терміном дії."""
    payload = {
        "sub": str(user_id),
        "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=minutes)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Декодування токена
def decode_token(token: str) -> TokenData:
    """Декодує токен та повертає корисне навантаження, або None у разі помилки."""

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_signature": True})
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)

        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception

    return token_data