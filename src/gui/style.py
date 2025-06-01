# src/gui/style.py

# الألوان الأساسية
PRIMARY_COLOR = "#007bff"  # أزرق ساطع
SECONDARY_COLOR = "#6c757d" # رمادي متوسط
ACCENT_COLOR = "#28a745"   # أخضر (يمكن أن يكون لون النجاح)
TEXT_COLOR = "#343a40"     # نص داكن
BACKGROUND_COLOR = "#f8f9fa" # خلفية فاتحة جداً
CARD_BACKGROUND_COLOR = "#ffffff" # خلفية البطاقات (أبيض)
BORDER_COLOR = "#dee2e6"   # لون حدود فاتح

# ألوان خاصة
DANGER_COLOR = "#dc3545"   # أحمر (للتحذير أو الحذف)
SUCCESS_COLOR = "#28a745"  # **أخضر للنجاح (هذا هو السطر المفقود)**
WARNING_COLOR = "#ffc107"  # **أصفر للتحذير (هذا هو السطر المفقود)**
INFO_COLOR = "#17a2b8"     # أزرق سماوي للمعلومات

# ألوان الخلفيات والحدود
BACKGROUND_COLOR = "#f8f9fa" # خلفية فاتحة جداً للبرنامج
HEADER_BACKGROUND_COLOR = PRIMARY_COLOR # خلفية الشريط العلوي
SIDEBAR_BACKGROUND_COLOR = "#343a40" # خلفية الشريط الجانبي (داكنة)
CARD_BACKGROUND_COLOR = "#ffffff" # خلفية البطاقات (أبيض)
BORDER_COLOR = "#dee2e6" # لون الحدود الفاتح

# ألوان النصوص
TEXT_COLOR = "#212529" # لون نص داكن (تقريباً أسود)
HEADER_TEXT_COLOR = "#ffffff" # لون النص في الهيدر (أبيض)
SIDEBAR_TEXT_COLOR = "#ffffff" # لون النص في الشريط الجانبي (أبيض)


# تنسيق QSS
QSS = f"""
/* الستايل العام للنافذة */
QMainWindow {{
    background-color: {BACKGROUND_COLOR};
}}

/* الستايل العام للعناصر */
QLabel, QWidget {{
    font-family: 'Arial';
    font-size: 14px;
    color: {TEXT_COLOR};       /* لون النص الافتراضي */
}}

/* الشريط العلوي (Header Bar) */
QFrame#HeaderBar {{
    background-color: {HEADER_BACKGROUND_COLOR};
    border-bottom: 1px solid {BORDER_COLOR};
    padding: 10px 20px;
}}

/* الشريط الجانبي (Sidebar) */
QFrame#Sidebar {{
    background-color: {SIDEBAR_BACKGROUND_COLOR};
    border-right: 1px solid #2b3035; /* حدود أغمق للشريط الجانبي */
    padding: 10px;
}}

/* أزرار الشريط الجانبي */
QPushButton.SidebarButton {{
    background-color: transparent;
    color: {SIDEBAR_TEXT_COLOR};
    border: none;
    padding: 10px 15px;
    text-align: right; /* محاذاة النص لليمين */
    font-size: 16px;
    font-weight: bold;
    border-radius: 8px;
}}

QPushButton.SidebarButton:hover {{
    background-color: #495057; /* لون أغمق عند التحويم */
}}

QPushButton.SidebarButton:checked {{
    background-color: {PRIMARY_COLOR}; /* لون أساسي عند التحديد */
    color: white;
}}

/* منطقة المحتوى المركزية */
QWidget#CentralContentArea {{
    background-color: {BACKGROUND_COLOR};
    padding: 20px;
}}

/* البطاقات (CardWidget) */
QFrame.CardWidget {{
    background-color: {CARD_BACKGROUND_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    padding: 15px;
}}

QFrame.CardWidget QLabel.Title {{
    font-size: 18px;
    font-weight: bold;
    color: {PRIMARY_COLOR};
    margin-bottom: 10px;
}}

/* شريط البحث */
QLineEdit.SearchBar {{
    padding: 8px 15px;
    border: 1px solid {BORDER_COLOR};
    border-radius: 20px; /* جعلها مستديرة أكثر */
    background-color: {CARD_BACKGROUND_COLOR};
    color: {TEXT_COLOR}; /* تصحيح هنا */
}}

QLineEdit.SearchBar:focus {{
    border: 1px solid {PRIMARY_COLOR};
}}

/* الأزرار العامة */
QPushButton {{
    background-color: {PRIMARY_COLOR};
    color: white;
    border: none;
    border-radius: 5px;
    padding: 8px 15px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: #0056b3; /* لون أزرق أغمق عند التحويم */
}}

QPushButton:pressed {{
    background-color: #004085; /* لون أزرق أغمق عند الضغط */
}}

/* أزرار التنبيهات والملف الشخصي في شريط الهيدر */
QPushButton#notification_button, QPushButton#profile_button {{
    background-color: transparent;
    border: none;
    padding: 5px;
}}

QPushButton#notification_button:hover, QPushButton#profile_button:hover {{
    background-color: rgba(255, 255, 255, 0.2); /* تأثير خفيف عند التحويم */
    border-radius: 5px;
}}

/* مركز التنبيهات المنبثق */
QFrame#NotificationCenterWidget {{
    background-color: {CARD_BACKGROUND_COLOR};
    border: 1px solid {BORDER_COLOR};
    border-radius: 10px;
    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); /* ظل خفيف */
}}
"""