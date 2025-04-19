import io
import os

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .config import settings
from .db import create_db_and_tables, engine
from .models.admin import AdminDB
from .models.user import UserDB
from .models.user_settings import UserSettingsDB
from .security import get_password_hash
from .routes import main_router


# ✅ قراءة نسخة التطبيق
def read(*paths, **kwargs):
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        return open_file.read().strip()


# ✅ إنشاء تطبيق FastAPI
app = FastAPI(
    title="Smart Life Organizer",
    description="Smart Life Organizer API helps you organize your tasks and habits with AI. 🚀",
    version=read("VERSION"),
    terms_of_service="http://smart_life_organizer.com/terms/",
    contact={
        "name": "author_name",
        "url": "http://smart_life_organizer.com/contact/",
        "email": "admin@example.com",
    },
    license_info={
        "name": "The Unlicense",
        "url": "https://unlicense.org",
    },
)

# ✅ إعداد CORS
if settings.server and settings.server.get("cors_origins", None):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.server["cors_origins"],
        allow_credentials=settings.server.get("cors_allow_credentials", True),
        allow_methods=settings.server.get("cors_allow_methods", ["*"]),
        allow_headers=settings.server.get("cors_allow_headers", ["*"]),
    )

# ✅ تسجيل الراوترات
app.include_router(main_router)

# ✅ نقطة ترحيب
@app.get("/")
def root():
    return {"message": "Welcome to the Smart Life Organizer API"}

# ✅ حدث التشغيل (Startup)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    with Session(engine) as session:
 

        # إنشاء user افتراضي
        if not session.query(UserDB).first():
            user = UserDB(
                username="azooz1",
                email="azoozazo59@gmail.com",
                password_hash=get_password_hash("azooz123"),
                first_name="azooz",
                last_name="User",
                phone_number="0594909409",
                gender="male",
                profile_picture=None,
                superuser=True
            )
            session.add(user)
            session.flush()  # للحصول على user_id

            # إعدادات افتراضية للمستخدم
            settings = UserSettingsDB(
                user_id=user.user_id,
                language="en",
                timezone="Asia/Riyadh",
                theme="light"
            )
            session.add(settings)

            print("✅ Default user and settings created.")
        else:
            print("ℹ️ User already exists.")

        session.commit()
