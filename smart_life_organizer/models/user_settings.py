from sqlalchemy import Column, Integer, String, Boolean, CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from ..db import Base  # ✅ استيراد Base فقط بدون إعادة تعريفه

class UserSettingsDB(Base):
    __tablename__ = "user_settings"

    settings_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    theme = Column(String(10), default="system")
    notification_preferences = Column(JSONB, default={})
    language = Column(String(10), default="en")
    time_zone = Column(String(50), default="UTC")
    ai_assistant_enabled = Column(Boolean, default=True)
    timezone = Column(String, default="UTC")  # ✅ أضف هذا السطر

    __table_args__ = (
        CheckConstraint("theme IN ('light', 'dark', 'system')", name="check_theme"),
        UniqueConstraint("user_id", name="idx_user_settings_user_id"),
    )

    user = relationship("UserDB", back_populates="settings")
