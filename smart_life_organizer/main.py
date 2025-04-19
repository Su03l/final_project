# main.py

from smart_life_organizer.app import app
from smart_life_organizer.db import create_db_and_tables, engine
from smart_life_organizer.models.admin import AdminDB
from smart_life_organizer.security import get_password_hash
from sqlalchemy.orm import Session

from smart_life_organizer.models.user import UserDB
from smart_life_organizer.security import get_password_hash
from sqlalchemy.orm import Session

@app.on_event("startup")
def create_default_users():
    with Session(engine) as session:
        existing = session.query(UserDB).filter(UserDB.username == "user2").first()
        if not existing:
            user = UserDB(
                username="user2",
                email="user2@example.com",
                password_hash=get_password_hash("user2pass"),
                first_name="User",
                last_name="Two",
                phone_number="0511111111",
                gender="female",
                superuser=False,
                is_active=True
            )
            session.add(user)
            print("✅ user2 created")
        
        existing3 = session.query(UserDB).filter(UserDB.username == "user3").first()
        if not existing3:
            user = UserDB(
                username="user3",
                email="user3@example.com",
                password_hash=get_password_hash("user3pass"),
                first_name="User",
                last_name="Three",
                phone_number="0522222222",
                gender="male",
                superuser=False,
                is_active=True
            )
            session.add(user)
            print("✅ user3 created")

        session.commit()
