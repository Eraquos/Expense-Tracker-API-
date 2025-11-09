from fastapi import FastAPI, Depends, HTTPException, Header
from database import session, User, Expense
from auth import decode_token, hash_password, verify_password, create_access_token

app = FastAPI()
@app.post("/register")
def register(name:str, email:str, password:str):
    if session.query(User).filter_by(email=email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    password_hash = hash_password(password)
    new_user = User(name=name, email=email, password_hash=password_hash)
    session.add(new_user)
    session.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(email: str, password: str):
    user = session.query(User).filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(user.id)
    return {"access_token": access_token}

@app.post("/expenses")
def add_expense(amount: int, category: str, description: str, date: str, authorization: str = Header(...)):
    user_id = decode_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    CATEGORIES = ["Groceries", "Leisure", "Electronics", "Utilities", "Clothing", "Health", "Others"]
    if category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="Invalid category")
    new_expense = Expense(user_id=user_id["user_id"], amount=amount, category=category, description=description, date=date)
    session.add(new_expense)
    session.commit()
    return {"message": "Expense added successfully"}
@app.get("/expenses")
def get_expenses(authorization: str = Header(...)):
    user_id = decode_token(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    expenses = session.query(Expense).filter_by(user_id=user_id["user_id"]).all()
    return {"expenses": [{"amount": exp.amount, "category": exp.category, "description": exp.description, "date": exp.date} for exp in expenses]}