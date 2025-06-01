# src/database/config.py
import os
from dotenv import load_dotenv

# قم بتحميل المتغيرات من ملف .env
load_dotenv()

# هنا سنحدد مسار قاعدة البيانات SQLite
# SQLite هي قاعدة بيانات خفيفة ومناسبة جداً للتطبيقات المكتبية.
# يمكننا لاحقاً التبديل إلى PostgreSQL أو MySQL إذا احتجنا لقاعدة بيانات خادم.

# مسار مجلد المشروع الرئيسي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# مسار ملف قاعدة البيانات SQLite
DATABASE_PATH = os.path.join(BASE_DIR, 'digital_justice.db')

# سلسلة الاتصال بـ SQLAlchemy
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# يمكن إضافة إعدادات لقاعدة بيانات PostgreSQL أو MySQL هنا إذا لزم الأمر مستقبلاً
# DATABASE_URL_POSTGRES = os.getenv("DATABASE_URL_POSTGRES")
# DATABASE_URL_MYSQL = os.getenv("DATABASE_URL_MYSQL")