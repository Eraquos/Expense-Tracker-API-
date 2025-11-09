from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

import psycopg2

engine = create_engine("postgresql://postgres:1234@localhost:5432/users_db")

Base = declarative_base()



class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True)
    password_hash = Column(String)
    expenses = relationship("Expense", back_populates="user")



class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer)
    category = Column(String)
    description = Column(String)
    date = Column(String)
    user = relationship("User", back_populates="expenses")



Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

