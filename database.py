from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.orm import Session # Імпортуємо для коректного типу в get_db

# Підключення до PostgreSQL
# engine = create_engine("postgresql://postgres:1234@localhost:5432/users_db", echo=True)
engine = create_engine("postgresql://postgres:1234@localhost:5434/users_db", echo=True)
Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модель користувача
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    expenses = relationship("Expense", back_populates="user")

# Модель витрати
class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date = Column(String, nullable=False)
    user = relationship("User", back_populates="expenses")

# Створює таблиці, якщо їх ще нема
Base.metadata.create_all(engine)