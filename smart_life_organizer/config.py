import os
from dynaconf import Dynaconf

# ✨ تحديد مسار مجلد هذا الملف (config.py)
HERE = os.path.dirname(os.path.abspath(__file__))

# ✅ تحميل الإعدادات باستخدام Dynaconf
settings = Dynaconf(
    envvar_prefix="smart_life_organizer",  # المقدمة لمتغيرات البيئة
    preload=[os.path.join(HERE, "default.toml")],  # ملف default.toml يحمل قيم افتراضية
    settings_files=["settings.toml", ".secrets.toml"],  # ملفات الإعدادات
    environments=["development", "production", "testing"],  # البيئات المدعومة
    env_switcher="smart_life_organizer_env",  # متغير البيئة للتبديل
    load_dotenv=False,  # منع تحميل .env بشكل لا يدد
)

"""
# استخدام ملف config.py في المشروع:

from smart_life_organizer.config import settings

## كيفية الوصول للقيم:
settings.SECRET_KEY
settings.db.uri
settings["db.uri"]
settings.get("DB__uri")

## لتغيير قيمة متغير:

♦ في settings.toml:
[development]
DEBUG=true

♦ كمتغير بيئة:
export smart_life_organizer_DEBUG=true

## لتغيير البيئة:
smart_life_organizer_ENV=production uvicorn smart_life_organizer.main:app

للمزيد من المعلومات:
https://dynaconf.com
"""