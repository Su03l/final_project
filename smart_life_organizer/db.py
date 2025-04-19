from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.declarative import declarative_base  # ⬅️ مهم لـ SQLAlchemy

from .config import settings

# ✅ إنشاء محرك قاعدة البيانات
engine = create_engine(
    settings.db.uri,
    echo=settings.db.echo,
    connect_args=settings.db.connect_args,
)

# ✅ تعريف Base الخاص بـ SQLAlchemy (لاستخدامه في AdminDB مثلاً)
Base = declarative_base()

# ✅ دالة لإنشاء الجداول الخاصة بـ SQLModel و SQLAlchemy معًا
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    Base.metadata.create_all(bind=engine)  # ⬅️ ضروري لإنشاء جداول AdminDB مثلاً

# ✅ دالة لإرجاع الجلسة (تُستخدم مع Depends)
def get_session():
    with Session(engine) as session:
        yield session

# ✅ اعتماد سريع للجلسة
ActiveSession = Depends(get_session)
