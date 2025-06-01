# digital_justice_desktop/src/gui/widgets.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QLineEdit, QScrollArea
)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize

class CardWidget(QFrame): # هذا هو السطر 8
    """
    بطاقة عرض معلومات قابلة للتخصيص.
    تستخدم QFrame لتطبيق الستايل الخاص بالبطاقات.
    """
    def __init__(self, title: str, content_widget: QWidget = None, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card") # تعيين الخاصية "class" لتطبيق الستايل من QSS (ملف style.py)
        # هذه الخاصية تسمح لنا بتطبيق CSS-like styling على QFrame محددة.

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.title_label = QLabel(title)
        # تعيين خاصية "class" لعنوان البطاقة
        self.title_label.setProperty("class", "CardTitle")
        self.layout.addWidget(self.title_label)

        if content_widget:
            # إذا تم تمرير ويدجت محتوى، أضفه مباشرة
            self.layout.addWidget(content_widget)
        else:
            # وإلا، ضع نصًا افتراضياً
            self.content_label = QLabel("هنا محتوى البطاقة...")
            self.layout.addWidget(self.content_label)

        self.setMinimumHeight(150) # ارتفاع افتراضي لكي تظهر البطاقة بشكل مناسب
        self.setMaximumHeight(300) # ارتفاع أقصى للبطاقة (يمكن تعديله)

class SidebarButton(QPushButton):
    """
    زر مخصص للشريط الجانبي مع أيقونة ونص.
    مصمم ليكون قابلاً للتفعيل (checkable) لتحديد الزر النشط.
    """
    def __init__(self, text: str, icon_path: str = None, parent=None):
        super().__init__(text, parent)
        # هذه الخاصية المخصصة "iconOnly" لا تستخدم مباشرة في QSS هنا،
        # ولكنها مفيدة لتنظيم الأزرار إذا كان هناك أكثر من نوع.
        self.setProperty("iconOnly", "false")

        if icon_path:
            # تحميل الأيقونة وتعيين حجمها
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(24, 24))
            # إضافة مسافات للنص لتبدو جيدة بجانب الأيقونة
            # هذه المسافات مهمة جداً لتدفق الـ RTL
            self.setText(f"   {text}")

        # جعل الزر قابلاً للتحديد/التنشيط (مثل زر الراديو)
        self.setCheckable(True)

class SearchBar(QLineEdit):
    """
    شريط بحث موحد وذكي.
    """
    def __init__(self, placeholder_text="ابحث في العدالة الرقمية...", parent=None):
        super().__init__(parent)
        # النص الذي يظهر في شريط البحث قبل الكتابة
        self.setPlaceholderText(placeholder_text)
        # زر صغير لمسح النص (يظهر تلقائياً عند وجود نص)
        self.setClearButtonEnabled(True)

class NotificationCenterWidget(QScrollArea):
    """
    ويدجت لمركز التنبيهات الموحد.
    تستخدم QScrollArea لتمكين التمرير إذا كان هناك الكثير من التنبيهات.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # تعيين اسم الكائن لتطبيق الستايل الخاص به من QSS
        self.setObjectName("NotificationCenter")
        # جعل المحتوى داخله قابلًا لتغيير الحجم
        self.setWidgetResizable(True)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        # محاذاة العناصر للأعلى داخل الـ ScrollArea
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # تعيين ويدجت المحتوى داخله
        self.setWidget(self.content_widget)

        # إضافة بعض التنبيهات التجريبية (يمكن حذفها لاحقاً واستبدالها ببيانات حقيقية)
        self.add_notification("جلسة قضية رقم 1234 (موكل: أحمد) اليوم الساعة 10:00 صباحاً في محكمة النقض.", "2025-05-31")
        self.add_notification("مهمة مستحقة: مراجعة عقد الإيجار في قضية رقم 5678.", "2025-05-30")
        self.add_notification("تحديث على قضية رقم 9101: تم إيداع مذكرة جديدة من الخصم.", "2025-05-31")

    def add_notification(self, message: str, date: str):
        """
        دالة لإضافة تنبيه جديد إلى مركز التنبيهات.
        كل تنبيه هو QFrame منفصل لتطبيق الستايل عليه.
        """
        notif_frame = QFrame()
        # تعيين خاصية "class" لتطبيق الستايل المحدد في QSS
        notif_frame.setProperty("class", "NotificationItem")
        notif_layout = QVBoxLayout(notif_frame)

        msg_label = QLabel(message)
        msg_label.setWordWrap(True) # لضمان التفاف النص الطويل داخل المساحة المتاحة
        date_label = QLabel(f"<small>بتاريخ: {date}</small>") # عرض التاريخ بخط أصغر قليلاً
        date_label.setStyleSheet("color: #6c757d;") # لون رمادي فاتح للتاريخ

        notif_layout.addWidget(msg_label)
        notif_layout.addWidget(date_label)
        # هوامش داخلية للتنبيه الواحد
        notif_layout.setContentsMargins(10, 5, 10, 5)

        self.content_layout.addWidget(notif_frame)