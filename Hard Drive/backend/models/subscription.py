# File: /Users/rick/CaseProject/backend/models/subscription.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.sqlite import JSON

from db.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    auth0_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    case_analyses = relationship("CaseAnalysis", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    plan_name = Column(String)
    plan_id = Column(String)
    status = Column(String)
    trial_end = Column(DateTime, nullable=True)
    current_period_start = Column(DateTime, nullable=True)
    current_period_end = Column(DateTime, nullable=True)
    monthly_quota = Column(Integer, default=0)
    remaining_quota = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="subscription")

class CaseAnalysis(Base):
    __tablename__ = "case_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_case = Column(JSON)
    prediction = Column(Text)
    similar_cases = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    user = relationship("User", back_populates="case_analyses")
