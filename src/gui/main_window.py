# src/gui/main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QStackedWidget, QMessageBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont # أضف QFont لاستخدامه في التنسيق

# استيراد الألوان والستايل
from gui.style import PRIMARY_COLOR, BACKGROUND_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR, CARD_BACKGROUND_COLOR

# استيراد الواجهات الرسومية المختلفة
from gui.clients_view import ClientsView
from gui.add_client_form import AddClientForm # لكي نتمكن من الوصول لنموذج الإضافة والتعديل
# from gui.power_of_attorney_view import PowerOfAttorneyView # افترض وجودها لاحقاً
# from gui.interactions_view import InteractionsView # افترض وجودها لاحقاً

# استيراد وظائف قاعدة البيانات
from database.db import SessionLocal

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة الشؤون القانونية الرقمي")
        self.setWindowIcon(QIcon('assets/icons/app_icon.png')) # تأكد من وجود الأيقونة
        self.setGeometry(100, 100, 1200, 800) # (x, y, width, height)

        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        # الشريط الجانبي (Sidebar)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(200)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 10) # حواف (padding)
        self.sidebar_layout.setSpacing(10) # المسافة بين الأزرار
        self.sidebar.setStyleSheet(f"background-color: {PRIMARY_COLOR}; border-right: 1px solid {BORDER_COLOR};")

        # شعار أو عنوان التطبيق في الشريط الجانبي
        logo_label = QLabel("نظام الإدارة")
        logo_label.setFont(QFont("Arial", 14, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: white; padding-bottom: 20px;")
        self.sidebar_layout.addWidget(logo_label)

        # أزرار التنقل في الشريط الجانبي
        self.btn_clients = self._create_sidebar_button("العملاء", "assets/icons/clients_icon.png")
        self.btn_power_of_attorney = self._create_sidebar_button("التوكيلات", "assets/icons/poa_icon.png")
        self.btn_interactions = self._create_sidebar_button("التفاعلات", "assets/icons/interactions_icon.png")
        self.btn_reports = self._create_sidebar_button("التقارير", "assets/icons/reports_icon.png")
        self.btn_settings = self._create_sidebar_button("الإعدادات", "assets/icons/settings_icon.png")

        self.sidebar_layout.addWidget(self.btn_clients)
        self.sidebar_layout.addWidget(self.btn_power_of_attorney)
        self.sidebar_layout.addWidget(self.btn_interactions)
        self.sidebar_layout.addWidget(self.btn_reports)
        self.sidebar_layout.addWidget(self.btn_settings)
        self.sidebar_layout.addStretch(1) # لدفع الأزرار للأعلى

        # المحتوى الرئيسي (Main Content Area)
        self.main_content = QWidget()
        self.main_layout = QVBoxLayout(self.main_content)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)

        # عنوان القسم الحالي
        self.current_section_title = QLabel("العملاء")
        self.current_section_title.setFont(QFont("Arial", 18, QFont.Bold))
        self.current_section_title.setStyleSheet(f"color: {PRIMARY_COLOR};")
        self.main_layout.addWidget(self.current_section_title)

        # QStackedWidget لعرض الواجهات المختلفة
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

        # تهيئة الواجهات وإضافتها إلى StackedWidget
        self.clients_view = ClientsView()
        self.stacked_widget.addWidget(self.clients_view) # الفهرس 0
        
        # تهيئة نموذج إضافة/تعديل العميل
        # قم بإنشاء instance واحد فقط لـ AddClientForm وتحديثه لاحقاً
        self.add_client_form = AddClientForm()
        self.stacked_widget.addWidget(self.add_client_form) # الفهرس 1

        # ربط الإشارات (Signals) بين الواجهات
        self.btn_clients.clicked.connect(self._show_clients_view)
        # قم بربط الإشارة الجديدة لتعديل العميل
        self.clients_view.edit_client_requested.connect(self._show_edit_client_form)
        self.clients_view.add_client_requested.connect(self._show_add_client_form) # ربط زر إضافة موكل
        
        # ربط إشارات نموذج الإضافة/التعديل
        self.add_client_form.client_saved.connect(self._handle_client_saved)
        self.add_client_form.cancel_requested.connect(self._return_to_clients_view)

        # التخطيط الرئيسي (Main Layout)
        central_widget = QWidget()
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.addWidget(self.sidebar)
        main_h_layout.addWidget(self.main_content)
        
        self.setCentralWidget(central_widget)

    def _create_sidebar_button(self, text, icon_path):
        button = QPushButton(text)
        button.setIcon(QIcon(icon_path)) # تعيين الأيقونة
        # **** هذا هو السطر الذي يحتاج للتعديل ****
        # يجب أن نقوم بتحويل الناتج إلى QSize
        icon_height = int(button.fontMetrics().height() * 1.5) # نحوله إلى عدد صحيح
        button.setIconSize(QSize(icon_height, icon_height)) # نستخدم QSize هنا
        button.setFixedHeight(40) # ارتفاع ثابت للزر
        button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 15px;
                color: white;
                border: none;
                border-radius: 5px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QPushButton:checked {
                background-color: rgba(255, 255, 255, 0.3);
                border-left: 3px solid white;
            }
        """)
        button.setCheckable(True) # لجعل الزر قابل للاختيار
        return button

    def apply_styles(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            QLabel {{
                color: {TEXT_COLOR};
            }}
        """)
        # تأكد من أن الأزرار الصحيحة هي المحددة افتراضيا عند بدء التشغيل
        self.btn_clients.setChecked(True)


    def _show_clients_view(self):
        self.current_section_title.setText("العملاء")
        self.stacked_widget.setCurrentWidget(self.clients_view)
        # تأكد من أن جميع الأزرار الأخرى غير محددة
        self.btn_clients.setChecked(True)
        self.btn_power_of_attorney.setChecked(False)
        self.btn_interactions.setChecked(False)
        self.btn_reports.setChecked(False)
        self.btn_settings.setChecked(False)
        self.clients_view.load_clients() # إعادة تحميل البيانات عند العودة للعرض

    def _show_add_client_form(self):
        self.current_section_title.setText("إضافة موكل جديد")
        # عند طلب إضافة موكل جديد، يجب أن يكون النموذج فارغاً
        # لذلك، قم بإنشاء instance جديد أو إعادة تهيئة الـ instance الحالي بدون client_to_edit
        self.add_client_form = AddClientForm(parent=self)
        # قم بإزالة النموذج القديم وإضافة الجديد إلى stacked_widget لتحديثه
        self.stacked_widget.addWidget(self.add_client_form)
        self.stacked_widget.setCurrentWidget(self.add_client_form)
        
        # ربط الإشارات مجدداً (مهم إذا كنت تعيد إنشاء النموذج)
        self.add_client_form.client_saved.connect(self._handle_client_saved)
        self.add_client_form.cancel_requested.connect(self._return_to_clients_view)
        
    def _show_edit_client_form(self, client_data):
        print(f"طلب تعديل الموكل: {client_data.full_name}")
        
        try:
            # عند طلب تعديل موكل، نقوم بإنشاء instance جديد لـ AddClientForm مع بيانات الموكل
            # هذا يضمن أن النموذج يتم تهيئته بشكل صحيح مع البيانات الجديدة في كل مرة
            self.add_client_form = AddClientForm(client_to_edit=client_data, parent=self)
            
            # يجب إزالة النموذج القديم من stacked_widget قبل إضافة الجديد
            # لتجنب تكدس النماذج وضمان عرض النموذج الصحيح
            old_widget = self.stacked_widget.widget(self.stacked_widget.indexOf(self.add_client_form))
            if old_widget:
                self.stacked_widget.removeWidget(old_widget)
                old_widget.deleteLater() # حذف الودجت القديم من الذاكرة

            self.stacked_widget.addWidget(self.add_client_form) # أضف النموذج الجديد
            self.stacked_widget.setCurrentWidget(self.add_client_form) # واعرضه

            # ربط إشارات نموذج الإضافة/التعديل مجدداً (مهم جداً عند إعادة إنشاء النموذج)
            self.add_client_form.client_saved.connect(self._handle_client_saved)
            self.add_client_form.cancel_requested.connect(self._return_to_clients_view)
            
            self.current_section_title.setText(f"تعديل بيانات: {client_data.full_name}")
            print("نموذج تعديل الموكل تم عرضه بنجاح.")

        except Exception as e:
            print(f"-------------------- حدث خطأ غير معالج في _show_edit_client_form! --------------------")
            print(f"نوع الخطأ: {type(e).__name__}")
            print(f"القيمة: {e}")
            import traceback
            traceback.print_exc() # لطباعة الـ traceback كاملاً
            print(f"----------------------------------------------------------")
            QMessageBox.critical(self, "خطأ في تعديل الموكل", f"حدث خطأ أثناء محاولة عرض نموذج تعديل الموكل: {e}")
            self.stacked_widget.setCurrentWidget(self.clients_view) # العودة إلى عرض العملاء لتجنب الاختفاء
            # تأكد من إغلاق جلسة AddClientForm إذا تم فتحها وحدث خطأ
            if hasattr(self, 'add_client_form') and self.add_client_form:
                self.add_client_form.close_db_session()


    def _handle_client_saved(self):
        QMessageBox.information(self, "حفظ", "تم حفظ بيانات الموكل بنجاح.")
        self._return_to_clients_view()

    def _return_to_clients_view(self):
        self.current_section_title.setText("العملاء")
        self.stacked_widget.setCurrentWidget(self.clients_view)
        self.clients_view.load_clients() # إعادة تحميل البيانات للتأكد من عرض التغييرات

    def closeEvent(self, event):
        # تأكد من إغلاق جلسة قاعدة البيانات عند إغلاق النافذة الرئيسية
        if hasattr(self.clients_view, 'db_session') and self.clients_view.db_session:
            self.clients_view.close_db_session()
        if hasattr(self, 'add_client_form') and self.add_client_form:
            self.add_client_form.close_db_session()
        super().closeEvent(event)