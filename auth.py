from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import secrets
import os

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
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=minutes)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Декодування токена
def decode_token(token: str):
    """Декодує токен та повертає корисне навантаження, або None у разі помилки."""
    try:
        # Видаляємо префікс 'Bearer ' якщо він присутній (хоча FastAPI це зазвичай робить сам)
        if token.startswith("Bearer "):
            token = token[7:]
            
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token structure or signature")
        return None