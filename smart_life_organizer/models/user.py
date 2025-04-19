from sqlalchemy import Column, Integer, String, Boolean, DateTime, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship  # ✅ مهم جداً
from sqlalchemy.ext.declarative import declarative_base
# models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..db import Base

class UserDB(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20))
    password_hash = Column(String(255), nullable=False)
    profile_picture = Column(String(255))
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    gender = Column(String(10))
    superuser = Column(Boolean, default=False)  # ✅ أضف هذا السطر

    # ✅ العلاقة مع جدول الإعدادات
    settings = relationship("UserSettingsDB", back_populates="user", uselist=False)

    __table_args__ = (
        CheckConstraint("gender IN ('male', 'female')", name="check_gender"),
    )

