from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ActivityLevel(enum.Enum):
    SEDENTARY = "sedentary"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class GoalStatus(enum.Enum):
    ON_TRACK = "on_track"
    MET = "met"
    MISSED = "missed"

class NotificationType(enum.Enum):
    ON_TRACK = "on_track"
    MET = "met"
    MISSED = "missed"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    weight = Column(Float, nullable=True)  # in kg
    age = Column(Integer, nullable=True)
    activity_level = Column(Enum(ActivityLevel), nullable=True)
    dietary_preferences = Column(Text, nullable=True)
    protein_goal = Column(Float, nullable=True)  # in grams per day
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meals = relationship("Meal", back_populates="user")
    daily_summaries = relationship("DailySummary", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Meal(Base):
    __tablename__ = "meals"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    foods_detected = Column(Text, nullable=True)  # JSON string of detected foods
    protein_estimate = Column(Float, nullable=False)  # in grams
    manual_adjustment = Column(Float, nullable=True)  # manual correction in grams
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="meals")

class DailySummary(Base):
    __tablename__ = "daily_summaries"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_protein = Column(Float, nullable=False, default=0.0)  # in grams
    goal = Column(Float, nullable=False)  # in grams
    status = Column(Enum(GoalStatus), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="daily_summaries")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    read = Column(Integer, default=0)  # 0 = unread, 1 = read
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="notifications") 