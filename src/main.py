# src/main.py
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt # **أضف هذا السطر**
from gui.main_window import MainWindow
from database.db import create_db_and_tables

# ... (باقي الكود) ...

# --- كود معالجة الاستثناءات (Exception Hook) ---
# هذا الجزء مهم جداً لتحديد سبب توقف البرنامج (Crashing)
sys._excepthook = sys.excepthook # حفظ معالج الاستثناءات الأصلي

# --- كود معالجة الاستثناءات (Exception Hook) ---
sys._excepthook = sys.excepthook 

def exception_hook(exctype, value, tb): # غيرت 'traceback' إلى 'tb' لتجنب تضارب الاسم مع المكتبة
    """
    يقوم هذا المعالج المخصص بطباعة تتبع الخطأ (Traceback) كاملاً 
    إلى سطر الأوامر (terminal) إذا حدث خطأ غير معالج في تطبيق PyQt.
    """
    print("-------------------- حدث خطأ غير معالج! --------------------")
    print(f"نوع الخطأ: {exctype.__name__}")
    print(f"القيمة: {value}")
    import traceback # **استيراد مكتبة traceback القياسية هنا**
    traceback.print_exception(exctype, value, tb) # استخدامها لطباعة الـ traceback
    print("----------------------------------------------------------")
    sys._excepthook(exctype, value, tb) # استدعاء المعالج الأصلي
    sys.exit(1) # الخروج من التطبيق بعد طباعة الخطأ

sys.excepthook = exception_hook
# -------------------------------------------------------------

def main():
    # إنشاء وتجهيز قاعدة البيانات والجداول
    create_db_and_tables()

    app = QApplication(sys.argv)

    # تأكد أن دعم RTL (من اليمين لليسار) مفعل على مستوى التطبيق كله
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()