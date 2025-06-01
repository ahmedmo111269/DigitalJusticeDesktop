# src/main.py
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QStackedWidget, QMenuBar, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize

# استيراد الوجهات والنماذج ووظائف قاعدة البيانات
from gui.clients_view import ClientsView
from gui.add_client_form import AddClientForm
from database.db import create_db_and_tables # استيراد الدالة الجديدة

# استيراد الألوان من الستايل
from gui.style import PRIMARY_COLOR, BACKGROUND_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR, DANGER_COLOR, CARD_BACKGROUND_COLOR

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تطبيق الإدارة القانونية الرقمية")
        self.setGeometry(100, 100, 1200, 800) # تعيين الحجم الافتراضي للنافذة

        self.setWindowIcon(QIcon('assets/icon.png')) # تأكد من وجود أيقونة مناسبة

        # تهيئة قاعدة البيانات والجداول
        create_db_and_tables() # استدعاء لإنشاء الجداول عند بدء التطبيق

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.clients_view = ClientsView()
        self.add_client_form = AddClientForm()

        self.stacked_widget.addWidget(self.clients_view) # Index 0
        self.stacked_widget.addWidget(self.add_client_form) # Index 1

        self.setup_connections()
        self.setup_menu()
        self.apply_stylesheet()

        # عرض واجهة العملاء عند بدء التشغيل
        self.show_clients_view()

    def setup_connections(self):
        self.clients_view.add_client_requested.connect(self.show_add_client_form)
        self.clients_view.edit_client_requested.connect(self.show_edit_client_form)
        self.clients_view.section_title_changed.connect(self.setWindowTitle) # لتغيير عنوان النافذة الرئيسية
        self.add_client_form.client_saved.connect(self.on_client_saved)
        self.add_client_form.cancel_requested.connect(self.show_clients_view) # للعودة من نموذج الإضافة

    def setup_menu(self):
        menubar = self.menuBar()

        # قائمة "ملف"
        file_menu = menubar.addMenu("ملف")
        exit_action = QAction(QIcon('assets/icons/exit_icon.png'), "خروج", self) # أضف أيقونة إذا وجدت
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # قائمة "العملاء"
        clients_menu = menubar.addMenu("العملاء")
        view_clients_action = QAction("عرض العملاء", self)
        view_clients_action.triggered.connect(self.show_clients_view)
        clients_menu.addAction(view_clients_action)

        add_client_action = QAction("إضافة عميل جديد", self)
        add_client_action.triggered.connect(self.show_add_client_form)
        clients_menu.addAction(add_client_action)

        # قائمة "المساعدة"
        help_menu = menubar.addMenu("مساعدة")
        about_action = QAction("حول البرنامج", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def apply_stylesheet(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            QMenuBar {{
                background-color: {PRIMARY_COLOR};
                color: {TEXT_COLOR};
                font-size: 14px;
            }}
            QMenuBar::item {{
                padding: 5px 15px;
                background: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {ACCENT_COLOR};
            }}
            QMenu {{
                background-color: {BACKGROUND_COLOR};
                border: 1px solid {BORDER_COLOR};
                color: {TEXT_COLOR};
            }}
            QMenu::item {{
                padding: 5px 20px;
            }}
            QMenu::item:selected {{
                background-color: {PRIMARY_COLOR};
                color: white;
            }}
            QMessageBox {{
                background-color: {CARD_BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            QMessageBox QLabel {{
                color: {TEXT_COLOR};
            }}
            QMessageBox QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
        """)

    def show_clients_view(self):
        self.stacked_widget.setCurrentWidget(self.clients_view)
        self.clients_view.section_title_changed.emit("قائمة العملاء")
        self.clients_view.load_clients() # تأكد من إعادة تحميل البيانات عند العودة للعرض

    def show_add_client_form(self):
        # عندما نطلب إضافة عميل جديد، نتأكد أن النموذج فارغ
        self.add_client_form = AddClientForm() # إعادة إنشاء النموذج لتفريغه
        self.add_client_form.client_saved.connect(self.on_client_saved)
        self.add_client_form.cancel_requested.connect(self.show_clients_view)
        # إزالة النموذج القديم وإضافة الجديد
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1)) # إزالة النموذج القديم في الفهرس 1
        self.stacked_widget.insertWidget(1, self.add_client_form) # إضافة النموذج الجديد في نفس الفهرس
        self.stacked_widget.setCurrentWidget(self.add_client_form)
        self.add_client_form.section_title_changed.emit("إضافة عميل جديد")

    def show_edit_client_form(self, client_id):
        # عند تعديل عميل، نمرر الـ ID
        self.add_client_form = AddClientForm(client_id_to_edit=client_id) # تمرير الـ ID هنا
        self.add_client_form.client_saved.connect(self.on_client_saved)
        self.add_client_form.cancel_requested.connect(self.show_clients_view)
        # إزالة النموذج القديم وإضافة الجديد
        self.stacked_widget.removeWidget(self.stacked_widget.widget(1)) # إزالة النموذج القديم في الفهرس 1
        self.stacked_widget.insertWidget(1, self.add_client_form) # إضافة النموذج الجديد في نفس الفهرس
        self.stacked_widget.setCurrentWidget(self.add_client_form)
        self.add_client_form.section_title_changed.emit("تعديل بيانات العميل")


    def on_client_saved(self):
        QMessageBox.information(self, "نجاح", "تم حفظ بيانات العميل بنجاح.")
        self.show_clients_view() # العودة إلى عرض العملاء وتحديثه

    def show_about_dialog(self):
        QMessageBox.about(self, "حول تطبيق الإدارة القانونية الرقمية",
                          "<h2>تطبيق الإدارة القانونية الرقمية</h2>"
                          "<p>الإصدار 1.0</p>"
                          "<p>تطبيق لإدارة العملاء والتوكيلات وأرقام التواصل.<br>"
                          "تم تطويره باستخدام PyQt5 و SQLAlchemy.</p>"
                          "<p>لمزيد من المعلومات، يرجى زيارة <a href='https://github.com/ahmedmo111269/DigitalJusticeDesktop'>GitHub Repository</a></p>")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())