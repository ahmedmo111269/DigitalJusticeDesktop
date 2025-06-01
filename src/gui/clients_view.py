# src/gui/clients_view.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMessageBox, QFrame, QSizePolicy, QSpacerItem, QAction, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QFont

from database.db import SessionLocal, get_db # استيراد get_db
from database.models.client import Client, ClientType
from database.models.client_contact_number import ClientContactNumber # أضف هذا الاستيراد
from database.models.power_of_attorney import PowerOfAttorney # أضف هذا الاستيراد
from gui.add_client_form import AddClientForm # لكي نتمكن من الوصول لنموذج الإضافة والتعديل

from sqlalchemy.orm import joinedload # مهم جداً لتحميل العلاقات

# استيراد الألوان والستايل
from gui.style import PRIMARY_COLOR, BACKGROUND_COLOR, CARD_BACKGROUND_COLOR, TEXT_COLOR, BORDER_COLOR, ACCENT_COLOR, DANGER_COLOR

class ClientsView(QWidget):
    # إشارات (Signals) للتواصل مع النافذة الرئيسية
    section_title_changed = pyqtSignal(str)
    add_client_requested = pyqtSignal()
    edit_client_requested = pyqtSignal(int) # إشارة جديدة: ترسل ID الموكل المراد تعديله
    delete_client_requested = pyqtSignal(int) # إشارة جديدة: ترسل ID الموكل المراد حذفه

    def __init__(self):
        super().__init__()
        self.db_session = None # ستتم تهيئة الجلسة عند الحاجة
        self.current_client_data = [] # لتخزين بيانات العملاء المعروضة

        self.setup_ui()
        self.load_clients() # تحميل البيانات عند بدء التشغيل

    def setup_ui(self):
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(20, 20, 20, 20)
        self.layout().setSpacing(15)

        # شريط البحث
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث عن عميل بالاسم أو الهوية الوطنية...")
        self.search_input.setFont(QFont("Arial", 10))
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 10px;
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                background-color: {CARD_BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            QLineEdit:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
        """)
        self.search_input.textChanged.connect(self.filter_clients)
        search_layout.addWidget(self.search_input)

        self.add_button = QPushButton("إضافة عميل")
        self.add_button.setIcon(QIcon('assets/icons/add_icon.png')) # تأكد من وجود الأيقونة
        self.add_button.clicked.connect(self.add_client_requested.emit)
        self.add_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
        """)
        search_layout.addWidget(self.add_button)

        self.layout().addLayout(search_layout)

        # جدول عرض العملاء
        self.clients_table = QTableWidget()
        self.clients_table.setColumnCount(6) # عدد الأعمدة
        self.clients_table.setHorizontalHeaderLabels([
            "الاسم الكامل", "نوع العميل", "الرقم القومي/التسجيل",
            "البريد الإلكتروني", "عدد أرقام التواصل", "عدد التوكيلات"
        ])
        self.clients_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.clients_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.clients_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {CARD_BACKGROUND_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                gridline-color: {BORDER_COLOR};
                color: {TEXT_COLOR};
            }}
            QHeaderView::section {{
                background-color: {PRIMARY_COLOR};
                color: white;
                padding: 8px;
                border: 1px solid {BORDER_COLOR};
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {BORDER_COLOR};
            }}
            QTableWidget::item:selected {{
                background-color: {ACCENT_COLOR};
                color: white;
            }}
        """)

        # تفعيل القائمة السياقية (right-click menu)
        self.clients_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.clients_table.customContextMenuRequested.connect(self.show_context_menu)

        self.layout().addWidget(self.clients_table)

        # زر العودة (للتنقل إذا كانت هذه ليست الواجهة الرئيسية)
        # self.back_button = QPushButton("العودة")
        # self.back_button.clicked.connect(self.go_back_requested.emit)
        # self.layout().addWidget(self.back_button)

    def show_context_menu(self, pos):
        """يعرض القائمة السياقية (زر الفأرة الأيمن) للعملاء."""
        # نتأكد أن هناك صفًا محددًا
        if not self.clients_table.selectedItems():
            return

        context_menu = QMenu(self)

        edit_action = QAction("تعديل العميل", self)
        edit_action.triggered.connect(self.edit_selected_client)
        context_menu.addAction(edit_action)

        delete_action = QAction("حذف العميل", self)
        delete_action.triggered.connect(self.delete_selected_client)
        context_menu.addAction(delete_action)

        context_menu.exec_(self.clients_table.mapToGlobal(pos))

    def load_clients(self):
        """يحمل بيانات العملاء من قاعدة البيانات ويعرضها في الجدول."""
        print("Attempting to load clients...") # لتصحيح الأخطاء
        session = next(get_db()) # استخدام الدالة الجديدة للحصول على جلسة
        try:
            # استخدام joinedload لتحميل العلاقات مسبقًا لتجنب مشكلات الجلسة المغلقة
            # .options(joinedload(Client.contact_numbers), joinedload(Client.power_of_attorneys))
            # هذا يضمن أن البيانات المرتبطة متاحة حتى بعد إغلاق الجلسة
            clients = session.query(Client).filter(Client.is_hidden == False).options(
                joinedload(Client.contact_numbers),
                joinedload(Client.power_of_attorneys)
            ).all()

            self.current_client_data = clients
            self.clients_table.setRowCount(len(clients))

            for row_idx, client in enumerate(clients):
                self.clients_table.setItem(row_idx, 0, QTableWidgetItem(client.full_name))
                self.clients_table.setItem(row_idx, 1, QTableWidgetItem(client.client_type.value))
                self.clients_table.setItem(row_idx, 2, QTableWidgetItem(client.national_id or client.company_registration_number or "N/A"))
                self.clients_table.setItem(row_idx, 3, QTableWidgetItem(client.email or "N/A"))
                
                # عرض عدد أرقام التواصل والتوكيلات
                contact_count = len(client.contact_numbers) if client.contact_numbers else 0
                poa_count = len(client.power_of_attorneys) if client.power_of_attorneys else 0
                self.clients_table.setItem(row_idx, 4, QTableWidgetItem(str(contact_count)))
                self.clients_table.setItem(row_idx, 5, QTableWidgetItem(str(poa_count)))
                
                # تخزين كائن العميل نفسه في خاصية UserRole للوصول السهل إليه لاحقًا
                # هذا مهم لربط الصف في الجدول بكائن العميل الفعلي
                self.clients_table.item(row_idx, 0).setData(Qt.UserRole, client)

        except Exception as e:
            QMessageBox.critical(self, "خطأ في التحميل", f"حدث خطأ أثناء تحميل العملاء: {e}")
            print(f"Error loading clients: {e}")
            import traceback
            traceback.print_exc() # طباعة تتبع الخطأ للمساعدة في التصحيح
        finally:
            # لا حاجة لإغلاق الجلسة هنا لأن get_db() تتعامل مع الإغلاق تلقائيًا
            pass

    def filter_clients(self):
        """يقوم بتصفية العملاء المعروضين بناءً على نص البحث."""
        search_text = self.search_input.text().strip().lower()
        
        # إذا كان حقل البحث فارغاً، أعد تحميل جميع العملاء
        if not search_text:
            self.load_clients()
            return

        filtered_clients = []
        session = next(get_db()) # استخدام الدالة الجديدة للحصول على جلسة
        try:
            clients_query = session.query(Client).filter(Client.is_hidden == False)
            if search_text:
                clients_query = clients_query.filter(
                    (Client.full_name.ilike(f'%{search_text}%')) |
                    (Client.national_id.ilike(f'%{search_text}%')) |
                    (Client.company_registration_number.ilike(f'%{search_text}%'))
                )
            
            # تأكد من تحميل العلاقات هنا أيضاً إذا كنت ستستخدمها في العرض المصفى
            clients_query = clients_query.options(
                joinedload(Client.contact_numbers),
                joinedload(Client.power_of_attorneys)
            )
            
            filtered_clients = clients_query.all()

            self.clients_table.setRowCount(len(filtered_clients))
            for row_idx, client in enumerate(filtered_clients):
                self.clients_table.setItem(row_idx, 0, QTableWidgetItem(client.full_name))
                self.clients_table.setItem(row_idx, 1, QTableWidgetItem(client.client_type.value))
                self.clients_table.setItem(row_idx, 2, QTableWidgetItem(client.national_id or client.company_registration_number or "N/A"))
                self.clients_table.setItem(row_idx, 3, QTableWidgetItem(client.email or "N/A"))
                
                contact_count = len(client.contact_numbers) if client.contact_numbers else 0
                poa_count = len(client.power_of_attorneys) if client.power_of_attorneys else 0
                self.clients_table.setItem(row_idx, 4, QTableWidgetItem(str(contact_count)))
                self.clients_table.setItem(row_idx, 5, QTableWidgetItem(str(poa_count)))
                
                self.clients_table.item(row_idx, 0).setData(Qt.UserRole, client)
        except Exception as e:
            QMessageBox.critical(self, "خطأ في التصفية", f"حدث خطأ أثناء تصفية العملاء: {e}")
            print(f"Error filtering clients: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pass # الجلسة تغلق تلقائيًا

    def edit_selected_client(self):
        """يطلق إشارة لتعديل العميل المحدد."""
        selected_rows = self.clients_table.selectionModel().selectedRows()
        if selected_rows:
            selected_row_index = selected_rows[0].row()
            # استخراج كائن العميل من UserRole
            client_to_edit = self.clients_table.item(selected_row_index, 0).data(Qt.UserRole)
            if client_to_edit:
                self.edit_client_requested.emit(client_to_edit.id) # نرسل الـ ID
        else:
            QMessageBox.warning(self, "تعديل موكل", "الرجاء تحديد موكل لتعديله.")

    def delete_selected_client(self):
        """يحذف العميل المحدد بعد تأكيد."""
        selected_rows = self.clients_table.selectionModel().selectedRows()
        if selected_rows:
            selected_row_index = selected_rows[0].row()
            selected_client = self.clients_table.item(selected_row_index, 0).data(Qt.UserRole)
            
            if not selected_client:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات العميل المحدد.")
                return

            reply = QMessageBox.question(self, "تأكيد الحذف",
                                         f"هل أنت متأكد من حذف العميل: {selected_client.full_name}؟\n"
                                         "لا يمكن التراجع عن هذا الإجراء.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                session = next(get_db()) # فتح جلسة جديدة للحذف
                try:
                    # يمكننا حذف الموكل فعلياً أو "إخفاؤه" فقط (soft delete)
                    client_to_delete = session.query(Client).get(selected_client.id)
                    if client_to_delete:
                        # الخيار الأكثر أماناً هو "الإخفاء" (soft delete)
                        # client_to_delete.is_hidden = True 
                        # session.add(client_to_delete) # لو أردت الإخفاء
                        
                        # للحذف الفعلي:
                        session.delete(client_to_delete) 
                        session.commit()
                        QMessageBox.information(self, "حذف موكل", "تم حذف الموكل بنجاح.")
                        self.load_clients() # إعادة تحميل الجدول
                except Exception as e:
                    session.rollback() # التراجع عن أي تغييرات في حالة الخطأ
                    QMessageBox.critical(self, "خطأ في الحذف", f"حدث خطأ أثناء حذف الموكل: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    pass # الجلسة تغلق تلقائيًا عند الخروج من get_db()
        else:
            QMessageBox.warning(self, "حذف موكل", "الرجاء تحديد موكل لحذفه.")

    def close_db_session(self):
        """
        إغلاق جلسة قاعدة البيانات إذا كانت مفتوحة.
        ** لم تعد ضرورية مع استخدام get_db() **
        """
        if self.db_session:
            self.db_session.close()

    def closeEvent(self, event):
        """يتم استدعاؤها عند إغلاق النافذة."""
        self.close_db_session() # إغلاق الجلسة قبل الإغلاق
        super().closeEvent(event)