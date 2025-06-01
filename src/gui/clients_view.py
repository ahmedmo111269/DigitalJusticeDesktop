# src/gui/clients_view.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from database.db import SessionLocal
from database.models.client import Client, ClientType
# from gui.add_client_form import AddClientForm # لم نعد نستورد هذا هنا

# استيراد الألوان والستايل
from gui.style import PRIMARY_COLOR, BACKGROUND_COLOR, CARD_BACKGROUND_COLOR, TEXT_COLOR, BORDER_COLOR, ACCENT_COLOR, DANGER_COLOR, SUCCESS_COLOR, WARNING_COLOR # أضفت SUCCESS_COLOR و WARNING_COLOR للستايل

# استيراد relationship من sqlalchemy.orm للعلاقات
from sqlalchemy.orm import relationship, joinedload

class ClientsView(QWidget):
    section_title_changed = pyqtSignal(str)
    add_client_requested = pyqtSignal()
    edit_client_requested = pyqtSignal(int) # ترسل ID الموكل المراد تعديله

    def __init__(self):
        super().__init__()
        self.db_session = None
        self.current_client_data = []

        self.setup_ui()
        self.load_clients()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0) # إزالة الهوامش الداخلية
        main_layout.setSpacing(15)

        # شريط البحث
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث عن موكل بالاسم أو الرقم القومي...")
        self.search_input.setFixedHeight(35)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {CARD_BACKGROUND_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                padding: 8px;
                color: {TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
        """)
        self.search_input.textChanged.connect(self._filter_clients)
        
        search_layout.addWidget(self.search_input)
        main_layout.addLayout(search_layout)

        # الأزرار العلوية (إضافة، تعديل، حذف)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.btn_add_client = QPushButton("إضافة موكل")
        self.btn_add_client.setIcon(QIcon('assets/icons/add_icon.png'))
        self.btn_add_client.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
        """)
        self.btn_add_client.clicked.connect(self.add_client_requested.emit) # ربط الزر

        self.btn_edit_client = QPushButton("تعديل موكل")
        self.btn_edit_client.setIcon(QIcon('assets/icons/edit_icon.png'))
        self.btn_edit_client.setStyleSheet(f"""
            QPushButton {{
                background-color: {WARNING_COLOR};
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {WARNING_COLOR};
                opacity: 0.9;
            }}
        """)
        self.btn_edit_client.clicked.connect(self._edit_selected_client) # ربط الزر
        
        self.btn_delete_client = QPushButton("حذف موكل")
        self.btn_delete_client.setIcon(QIcon('assets/icons/delete_icon.png'))
        self.btn_delete_client.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER_COLOR};
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {DANGER_COLOR};
                opacity: 0.9;
            }}
        """)
        self.btn_delete_client.clicked.connect(self._delete_selected_client) # ربط الزر

        buttons_layout.addWidget(self.btn_add_client)
        buttons_layout.addWidget(self.btn_edit_client)
        buttons_layout.addWidget(self.btn_delete_client)
        buttons_layout.addStretch(1) # لدفع الأزرار إلى اليسار
        main_layout.addLayout(buttons_layout)

        # جدول عرض العملاء
        self.client_table = QTableWidget()
        self.client_table.setColumnCount(4) # ID, الاسم, النوع, الرقم الأساسي
        self.client_table.setHorizontalHeaderLabels(["ID", "الاسم الكامل", "النوع", "رقم الاتصال الرئيسي"])
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # توزيع الأعمدة بالتساوي
        self.client_table.setSelectionBehavior(QAbstractItemView.SelectRows) # تحديد صف كامل
        self.client_table.setEditTriggers(QAbstractItemView.NoEditTriggers) # منع التعديل المباشر
        
        self.client_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BACKGROUND_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                selection-background-color: {ACCENT_COLOR};
                selection-color: white;
                color: {TEXT_COLOR};
            }}
            QHeaderView::section {{
                background-color: {PRIMARY_COLOR};
                color: white;
                padding: 5px;
                border: 1px solid {BORDER_COLOR};
            }}
            QTableWidget::item {{
                padding: 5px;
            }}
        """)
        self.client_table.itemDoubleClicked.connect(self._edit_selected_client) # تعديل عند النقر المزدوج على أي عنصر في الصف

        main_layout.addWidget(self.client_table)

    def _load_clients_data(self):
        self.close_db_session() # أغلق أي جلسة سابقة
        self.db_session = SessionLocal() # افتح جلسة جديدة
        try:
            # هنا نحمل العملاء مع أرقام الاتصال لنتجنب Lazy Loading خارج الجلسة
            clients = self.db_session.query(Client).options(relationship("contact_numbers")).all()
            self.current_client_data = clients # تخزين الكائنات الحقيقية هنا
        except Exception as e:
            QMessageBox.critical(self, "خطأ في قاعدة البيانات", f"حدث خطأ أثناء تحميل العملاء: {e}")
            self.current_client_data = []
        finally:
            # لا نغلق الجلسة هنا لأننا قد نحتاج الوصول إلى الكائنات لاحقاً في العرض
            # ولكن تأكد أن MainWindow تغلق الجلسة عند إغلاق التطبيق.
            pass

    def load_clients(self):
        self._load_clients_data() # تحميل البيانات
        self._filter_clients() # إعادة فلترة لعرض الكل مبدئياً

    def _filter_clients(self):
        search_text = self.search_input.text().strip().lower()
        
        filtered_clients = []
        if search_text:
            for client in self.current_client_data:
                # البحث في الاسم الكامل أو الرقم القومي أو الرقم الرئيسي
                if (search_text in client.full_name.lower() or
                    (client.national_id and search_text in client.national_id.lower())):
                    filtered_clients.append(client)
                else: # البحث في أرقام الاتصال
                    for contact in client.contact_numbers:
                        if search_text in contact.number.lower():
                            filtered_clients.append(client)
                            break # إذا وجدنا تطابقًا، لا داعي للبحث في بقية الأرقام
        else:
            filtered_clients = self.current_client_data # عرض كل العملاء إذا كان شريط البحث فارغاً

        self.client_table.setRowCount(len(filtered_clients))
        for row, client in enumerate(filtered_clients):
            self.client_table.setItem(row, 0, QTableWidgetItem(str(client.id)))
            self.client_table.setItem(row, 1, QTableWidgetItem(client.full_name))
            self.client_table.setItem(row, 2, QTableWidgetItem(client.client_type.value))
            
            primary_number = "غير متاح"
            if client.contact_numbers:
                for contact in client.contact_numbers:
                    # يجب أن يكون عمود is_primary موجوداً في جدول ClientContactNumber
                    # تأكد أنك أضفته في ملف models/client_contact_number.py
                    if hasattr(contact, 'is_primary') and contact.is_primary:
                        primary_number = contact.number
                        break
                if primary_number == "غير متاح" and client.contact_numbers: # إذا لم نجد رئيسي، اعرض أول رقم
                    primary_number = client.contact_numbers[0].number
            self.client_table.setItem(row, 3, QTableWidgetItem(primary_number))

            self.client_table.item(row, 0).setData(Qt.UserRole, client) 

        self.client_table.resizeColumnsToContents()
        self.client_table.resizeRowsToContents()

    def _edit_selected_client(self):
        selected_items = self.client_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            selected_client_id = self.client_table.item(row, 0).data(Qt.UserRole).id # الحصول على الـ ID
            if selected_client_id is not None:
                self.edit_client_requested.emit(selected_client_id)
            else:
                QMessageBox.warning(self, "تعديل موكل", "البيانات المختارة غير صالحة (ID غير موجود).")
        else:
            QMessageBox.warning(self, "تعديل موكل", "الرجاء تحديد موكل لتعديله.")

    def _delete_selected_client(self):
        selected_items = self.client_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            selected_client = self.client_table.item(row, 0).data(Qt.UserRole)
            if selected_client:
                reply = QMessageBox.question(self, "تأكيد الحذف",
                                             f"هل أنت متأكد من حذف الموكل '{selected_client.full_name}'؟\n"
                                             "سيتم حذف جميع أرقام الاتصال والتوكيلات والتفاعلات المرتبطة بهذا الموكل.",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    self.db_session = SessionLocal() # فتح جلسة جديدة للحذف
                    try:
                        client_to_delete = self.db_session.query(Client).get(selected_client.id)
                        if client_to_delete:
                            self.db_session.delete(client_to_delete)
                            self.db_session.commit()
                            QMessageBox.information(self, "حذف موكل", "تم حذف الموكل بنجاح.")
                            self.load_clients()
                    except Exception as e:
                        self.db_session.rollback()
                        QMessageBox.critical(self, "خطأ في الحذف", f"حدث خطأ أثناء حذف الموكل: {e}")
                    finally:
                        self.close_db_session()
            else:
                QMessageBox.warning(self, "حذف موكل", "البيانات المختارة غير صالحة.")
        else:
            QMessageBox.warning(self, "حذف موكل", "الرجاء تحديد موكل لحذفه.")

    def close_db_session(self):
        if self.db_session:
            self.db_session.close()