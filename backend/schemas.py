from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    MODERATE = "moderate"
    ACTIVE = "active"
    VERY_ACTIVE = "very_active"

class GoalStatus(str, Enum):
    ON_TRACK = "on_track"
    MET = "met"
    MISSED = "missed"

class NotificationType(str, Enum):
    ON_TRACK = "on_track"
    MET = "met"
    MISSED = "missed"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    weight: Optional[float]
    age: Optional[int]
    activity_level: Optional[ActivityLevel]
    dietary_preferences: Optional[str]

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    weight: Optional[float]
    age: Optional[int]
    activity_level: Optional[ActivityLevel]
    dietary_preferences: Optional[str]
    protein_goal: Optional[float]

class User(UserBase):
    id: int
    protein_goal: Optional[float]
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class MealBase(BaseModel):
    protein_estimate: float
    manual_adjustment: Optional[float]

class MealCreate(MealBase):
    user_id: int
    image_url: str
    foods_detected: Optional[str]

class Meal(MealBase):
    id: int
    user_id: int
    image_url: str
    timestamp: datetime
    foods_detected: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class DailySummaryBase(BaseModel):
    date: date
    total_protein: float
    goal: float
    status: GoalStatus

class DailySummaryCreate(BaseModel):
    user_id: int
    date: date

class DailySummary(DailySummaryBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    date: date
    type: NotificationType
    message: str
    read: bool = False

class Notification(NotificationBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True 