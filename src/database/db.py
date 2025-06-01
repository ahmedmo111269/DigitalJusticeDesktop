# src/database/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# استيراد إعدادات قاعدة البيانات
from database.config import DATABASE_URL, BASE_DIR, DATABASE_PATH

# 1. إنشاء محرك قاعدة البيانات (Engine)
# echo=True لعرض استعلامات SQL في الطرفية (مفيد للتصحيح)
engine = create_engine(DATABASE_URL, echo=True)

# 2. إنشاء قاعدة declarative_base
# هذه هي الفئة الأساسية التي سترث منها جميع نماذج (Models) قاعدة البيانات.
Base = declarative_base()
# **تأكد أن هذا السطر موجود وهو الذي يستورد ملف __init__.py الخاص بالنماذج**
# يجب أن يتم الاستيراد بعد تعريف Base
import database.models.__init__ # هذا السطر يضمن أن SQLAlchemy ترى جميع النماذج

# 3. إنشاء SessionLocal
# هذا سيستخدم لإنشاء جلسات (Sessions) فردية للتفاعل مع قاعدة البيانات.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# دالة مساعدة لإنشاء جميع الجداول المعرفة في Base
def create_db_and_tables():
    # لضمان إنشاء مجلد البيانات إذا كان غير موجود
    data_dir = os.path.dirname(DATABASE_PATH)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    print(f"Creating database tables at: {DATABASE_PATH}")
    # Base.metadata.create_all() ستبحث عن جميع النماذج التي ترث من Base
    # وتنشئ الجداول المقابلة لها في قاعدة البيانات.
    Base.metadata.create_all(bind=engine)
    print("Database tables created/checked.")

# دالة مساعدة للحصول على جلسة قاعدة بيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()