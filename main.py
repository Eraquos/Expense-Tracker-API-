from fastapi import FastAPI, HTTPException, Body, Header, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Session as DBSession, engine, User, Expense
from auth import hash_password, verify_password, create_access_token, decode_token
from typing import List, Dict, Any


app = FastAPI()

CATEGORIES = ["Groceries", "Leisure", "Electronics", "Utilities", "Clothing", "Health", "Others"]

# Функція для отримання сесії бази даних (виправлено)
def get_db():
    """Створює нову сесію бази даних та закриває її після використання."""
    db = DBSession(bind=engine)
    try:
        yield db
    finally:
        db.close()

# Схеми Pydantic для валідації
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# НОВА МОДЕЛЬ: Використовуйте її для POST /expenses
class ExpenseCreate(BaseModel):
    amount: float
    category: str
    description: str = ""
    date: str

class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    date: str
    description: str
    
    class Config:
        # Дозволяє FastAPI читати дані з SQLAlchemy моделі
        from_attributes = True

# ---------------- Register ----------------
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Реєстрація нового користувача."""
    if db.query(User).filter_by(email=user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    password_hash = hash_password(user.password)
    new_user = User(name=user.name, email=user.email, password_hash=password_hash)

    try:
        db.add(new_user)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error during registration: {str(e)}")
    
    return {"message": "User registered successfully"}

# ---------------- Login ----------------
@app.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    """Вхід користувача та генерація JWT токена."""
    user = db.query(User).filter_by(email=data.email).first()
    
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(user_id=user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------- Add Expense ----------------
@app.post("/expenses", response_model=ExpenseResponse) # Використовуємо response_model
def add_expense(
    expense_data: ExpenseCreate, # ВИКОРИСТОВУЄМО ОДИН ОБ'ЄКТ PYDANTIC
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    """Додає нову витрату для аутентифікованого користувача."""
    
    # 1. Аутентифікація
    token_data = decode_token(authorization)
    if not token_data or "user_id" not in token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = token_data["user_id"]

    # 2. Перевірка валідності категорії
    if expense_data.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Invalid category. Must be one of: {', '.join(CATEGORIES)}")

    # 3. Створення об'єкта витрати
    new_expense = Expense(
        user_id=user_id,
        amount=expense_data.amount,
        category=expense_data.category,
        description=expense_data.description,
        date=expense_data.date
    )

    # 4. Збереження до бази даних
    try:
        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error when adding expense: {str(e)}")

    # Повертаємо успішну відповідь
    return new_expense # FastAPI автоматично перетворить це на ExpenseResponse


# ---------------- Get Expenses ----------------
@app.get("/expenses", response_model=List[ExpenseResponse])
def get_expenses(authorization: str = Header(...), db: Session = Depends(get_db)):
    """Отримує список усіх витрат для аутентифікованого користувача."""
    token_data = decode_token(authorization)
    if not token_data or "user_id" not in token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_id = token_data["user_id"]

    # Отримання витрат із бази даних
    expenses = db.query(Expense).filter_by(user_id=user_id).all()
    
    return expenses