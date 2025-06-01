# src/gui/add_client_form.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QDateEdit, QScrollArea, QFrame, QMessageBox,
    QCheckBox, QGroupBox, QSpacerItem, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize
from PyQt5.QtGui import QIcon, QFont

# استيراد الألوان من الستايل
from gui.style import PRIMARY_COLOR, BACKGROUND_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR, DANGER_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, WARNING_COLOR, CARD_BACKGROUND_COLOR

# استيراد وظائف وقاعدة البيانات والنماذج
from database.db import SessionLocal, get_db # استيراد get_db
from database.models.client import Client, ClientType
from database.models.client_contact_number import ClientContactNumber, ContactType
from datetime import datetime

from sqlalchemy.orm import joinedload # مهم لتحميل العلاقات عند التعديل

class AddClientForm(QWidget):
    # إشارة تصدر عند حفظ موكل جديد بنجاح
    client_saved = pyqtSignal()
    # إشارة تصدر عند طلب الإلغاء (للعودة إلى العرض السابق)
    cancel_requested = pyqtSignal()
    # إشارة لتغيير عنوان القسم في النافذة الرئيسية
    section_title_changed = pyqtSignal(str)


    def __init__(self, client_id_to_edit=None, parent=None):
        super().__init__(parent)
        self.db_session = None # تهيئة الجلسة لاحقاً عند الحاجة
        self.client_id_to_edit = client_id_to_edit
        self.client_to_edit = None

        self.contact_number_widgets = [] # لتخزين عناصر واجهة المستخدم لأرقام التواصل

        self.setup_ui()
        self.apply_stylesheet()
        if self.client_id_to_edit:
            self.load_client_for_edit()


    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # عنوان النموذج
        self.title_label = QLabel("إضافة عميل جديد")
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"color: {PRIMARY_COLOR};")
        main_layout.addWidget(self.title_label)

        # Scroll Area for the form content
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Disable horizontal scroll bar
        main_layout.addWidget(scroll_area)

        form_widget = QWidget()
        self.form_layout = QVBoxLayout(form_widget)
        self.form_layout.setContentsMargins(0, 0, 0, 0) # No extra margins for the form content
        self.form_layout.setSpacing(10)
        scroll_area.setWidget(form_widget)

        # General Info Group Box
        general_info_group = QGroupBox("المعلومات الأساسية")
        general_info_layout = QGridLayout()
        general_info_group.setLayout(general_info_layout)
        self.form_layout.addWidget(general_info_group)

        # Full Name
        general_info_layout.addWidget(QLabel("الاسم الكامل:"), 0, 0)
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("أدخل الاسم الكامل للعميل")
        general_info_layout.addWidget(self.full_name_input, 0, 1)

        # Client Type
        general_info_layout.addWidget(QLabel("نوع العميل:"), 1, 0)
        self.client_type_combo = QComboBox()
        for client_type in ClientType:
            self.client_type_combo.addItem(client_type.value, client_type)
        self.client_type_combo.currentIndexChanged.connect(self.toggle_client_type_fields)
        general_info_layout.addWidget(self.client_type_combo, 1, 1)

        # Fields for Individual Clients
        self.national_id_label = QLabel("الرقم القومي:")
        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("أدخل الرقم القومي")
        general_info_layout.addWidget(self.national_id_label, 2, 0)
        general_info_layout.addWidget(self.national_id_input, 2, 1)

        self.birth_date_label = QLabel("تاريخ الميلاد:")
        self.birth_date_input = QDateEdit(calendarPopup=True)
        self.birth_date_input.setDate(QDate.currentDate())
        self.birth_date_input.setDisplayFormat("yyyy-MM-dd")
        general_info_layout.addWidget(self.birth_date_label, 3, 0)
        general_info_layout.addWidget(self.birth_date_input, 3, 1)

        # Fields for Company/Government Entity
        self.company_name_label = QLabel("اسم الشركة/الجهة:")
        self.company_name_input = QLineEdit()
        self.company_name_input.setPlaceholderText("أدخل اسم الشركة أو الجهة")
        general_info_layout.addWidget(self.company_name_label, 4, 0)
        general_info_layout.addWidget(self.company_name_input, 4, 1)
        self.company_name_label.hide()
        self.company_name_input.hide()

        self.company_registration_number_label = QLabel("رقم التسجيل التجاري:")
        self.company_registration_number_input = QLineEdit()
        self.company_registration_number_input.setPlaceholderText("أدخل رقم التسجيل التجاري")
        general_info_layout.addWidget(self.company_registration_number_label, 5, 0)
        general_info_layout.addWidget(self.company_registration_number_input, 5, 1)
        self.company_registration_number_label.hide()
        self.company_registration_number_input.hide()

        self.company_logo_path_label = QLabel("مسار شعار الشركة:")
        self.company_logo_path_input = QLineEdit()
        self.company_logo_path_input.setPlaceholderText("أدخل مسار شعار الشركة (اختياري)")
        general_info_layout.addWidget(self.company_logo_path_label, 6, 0)
        general_info_layout.addWidget(self.company_logo_path_input, 6, 1)
        self.company_logo_path_label.hide()
        self.company_logo_path_input.hide()

        self.legal_representative_name_label = QLabel("اسم الممثل القانوني:")
        self.legal_representative_name_input = QLineEdit()
        self.legal_representative_name_input.setPlaceholderText("أدخل اسم الممثل القانوني")
        general_info_layout.addWidget(self.legal_representative_name_label, 7, 0)
        general_info_layout.addWidget(self.legal_representative_name_input, 7, 1)
        self.legal_representative_name_label.hide()
        self.legal_representative_name_input.hide()

        self.legal_representative_title_label = QLabel("صفة الممثل:")
        self.legal_representative_title_input = QLineEdit()
        self.legal_representative_title_input.setPlaceholderText("أدخل صفة الممثل القانوني")
        general_info_layout.addWidget(self.legal_representative_title_label, 8, 0)
        general_info_layout.addWidget(self.legal_representative_title_input, 8, 1)
        self.legal_representative_title_label.hide()
        self.legal_representative_title_input.hide()

        # Contact Info Group Box
        contact_info_group = QGroupBox("معلومات الاتصال")
        contact_info_layout = QGridLayout()
        contact_info_group.setLayout(contact_info_layout)
        self.form_layout.addWidget(contact_info_group)

        contact_info_layout.addWidget(QLabel("العنوان:"), 0, 0)
        self.address_input = QTextEdit()
        self.address_input.setPlaceholderText("أدخل عنوان العميل")
        self.address_input.setFixedSize(QSize(300, 70))
        contact_info_layout.addWidget(self.address_input, 0, 1)

        contact_info_layout.addWidget(QLabel("البريد الإلكتروني:"), 1, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("أدخل البريد الإلكتروني")
        contact_info_layout.addWidget(self.email_input, 1, 1)
        
        # Phone Numbers Dynamic Section
        self.phone_numbers_group = QGroupBox("أرقام التواصل")
        self.phone_numbers_layout = QVBoxLayout()
        self.phone_numbers_group.setLayout(self.phone_numbers_layout)
        self.form_layout.addWidget(self.phone_numbers_group)
        
        self.add_phone_button = QPushButton("إضافة رقم تواصل جديد")
        self.add_phone_button.clicked.connect(self.add_phone_number_field)
        self.phone_numbers_layout.addWidget(self.add_phone_button)
        self.add_phone_number_field() # Add one phone number field by default

        # Other Info Group Box
        other_info_group = QGroupBox("معلومات أخرى")
        other_info_layout = QGridLayout()
        other_info_group.setLayout(other_info_layout)
        self.form_layout.addWidget(other_info_group)

        other_info_layout.addWidget(QLabel("جهة العمل:"), 0, 0)
        self.work_employer_input = QLineEdit()
        self.work_employer_input.setPlaceholderText("أدخل جهة العمل (اختياري)")
        other_info_layout.addWidget(self.work_employer_input, 0, 1)

        other_info_layout.addWidget(QLabel("مصدر التواصل:"), 1, 0)
        self.source_of_contact_input = QLineEdit()
        self.source_of_contact_input.setPlaceholderText("كيف عرف المكتب بالعميل؟ (اختياري)")
        other_info_layout.addWidget(self.source_of_contact_input, 1, 1)

        other_info_layout.addWidget(QLabel("ملاحظات:"), 2, 0)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("ملاحظات إضافية عن العميل (اختياري)")
        self.notes_input.setFixedSize(QSize(300, 70))
        other_info_layout.addWidget(self.notes_input, 2, 1)

        # Action Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("حفظ")
        self.save_button.setIcon(QIcon('assets/icons/save_icon.png')) # تأكد من وجود الأيقونة
        self.save_button.clicked.connect(self.save_client)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setIcon(QIcon('assets/icons/cancel_icon.png')) # تأكد من وجود الأيقونة
        self.cancel_button.clicked.connect(self.cancel_requested.emit)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)
        
        # Initial toggle based on default client type
        self.toggle_client_type_fields(self.client_type_combo.currentIndex())


    def apply_stylesheet(self):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
                font-family: Arial;
                font-size: 10pt;
            }}
            QGroupBox {{
                background-color: {CARD_BACKGROUND_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 20px;
                font-size: 11pt;
                font-weight: bold;
                color: {PRIMARY_COLOR};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: {CARD_BACKGROUND_COLOR};
                border-radius: 5px;
            }}
            QLabel {{
                color: {TEXT_COLOR};
                font-weight: bold;
                padding-right: 5px;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                padding: 8px;
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 1px solid {ACCENT_COLOR};
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QPushButton:hover {{
                background-color: {ACCENT_COLOR};
            }}
            QPushButton#cancel_button {{ /* Example if you want a specific style for cancel */
                background-color: {DANGER_COLOR};
            }}
            QPushButton#cancel_button:hover {{
                background-color: #A32D2D;
            }}
            QScrollArea {{
                border: none;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top left;
                width: 20px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {BORDER_COLOR};
                selection-background-color: {ACCENT_COLOR};
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top left;
                width: 20px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
        """)

    def toggle_client_type_fields(self, index):
        selected_type = self.client_type_combo.itemData(index)
        
        # Hide all corporate fields
        self.company_name_label.hide()
        self.company_name_input.hide()
        self.company_registration_number_label.hide()
        self.company_registration_number_input.hide()
        self.company_logo_path_label.hide()
        self.company_logo_path_input.hide()
        self.legal_representative_name_label.hide()
        self.legal_representative_name_input.hide()
        self.legal_representative_title_label.hide()
        self.legal_representative_title_input.hide()

        # Hide all individual fields
        self.national_id_label.hide()
        self.national_id_input.hide()
        self.birth_date_label.hide()
        self.birth_date_input.hide()

        if selected_type == ClientType.INDIVIDUAL:
            self.national_id_label.show()
            self.national_id_input.show()
            self.birth_date_label.show()
            self.birth_date_input.show()
        elif selected_type in [ClientType.COMPANY, ClientType.GOVERNMENT_ENTITY]:
            self.company_name_label.show()
            self.company_name_input.show()
            self.company_registration_number_label.show()
            self.company_registration_number_input.show()
            self.company_logo_path_label.show()
            self.company_logo_path_input.show()
            self.legal_representative_name_label.show()
            self.legal_representative_name_input.show()
            self.legal_representative_title_label.show()
            self.legal_representative_title_input.show()

    def add_phone_number_field(self, number="", contact_type_enum=ContactType.MOBILE, is_primary=False):
        phone_layout = QHBoxLayout()
        
        phone_input = QLineEdit(number)
        phone_input.setPlaceholderText("رقم التواصل")
        phone_input.setStyleSheet(f"QLineEdit {{background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};}}")

        type_combo = QComboBox()
        for c_type in ContactType:
            type_combo.addItem(c_type.value, c_type)
        type_combo.setCurrentIndex(type_combo.findData(contact_type_enum))
        type_combo.setStyleSheet(f"QComboBox {{background-color: {BACKGROUND_COLOR}; color: {TEXT_COLOR};}}")

        primary_checkbox = QCheckBox("أساسي")
        primary_checkbox.setChecked(is_primary)
        primary_checkbox.setStyleSheet(f"QCheckBox {{color: {TEXT_COLOR};}}")

        remove_button = QPushButton("إزالة")
        remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER_COLOR};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #A32D2D;
            }}
        """)
        remove_button.clicked.connect(lambda: self.remove_phone_number_field(phone_layout))

        phone_layout.addWidget(phone_input)
        phone_layout.addWidget(type_combo)
        phone_layout.addWidget(primary_checkbox)
        phone_layout.addWidget(remove_button)
        
        # Insert the new phone field before the "add phone" button
        # This keeps the "add phone" button at the bottom
        self.phone_numbers_layout.insertLayout(self.phone_numbers_layout.count() - 1, phone_layout)
        
        self.contact_number_widgets.append({
            "layout": phone_layout,
            "phone_input": phone_input,
            "type_combo": type_combo,
            "primary_checkbox": primary_checkbox
        })

    def remove_phone_number_field(self, layout_to_remove):
        for i in range(len(self.contact_number_widgets)):
            if self.contact_number_widgets[i]["layout"] == layout_to_remove:
                # Remove widgets from layout
                while layout_to_remove.count():
                    item = layout_to_remove.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                # Remove layout from parent layout
                self.phone_numbers_layout.removeItem(layout_to_remove)
                self.contact_number_widgets.pop(i)
                break
        
        # إذا لم يعد هناك أي أرقام، أضف حقلاً فارغاً مرة أخرى
        if not self.contact_number_widgets:
            self.add_phone_number_field()


    def load_client_for_edit(self):
        """يحمل بيانات العميل الحالي لملء النموذج."""
        self.title_label.setText("تعديل بيانات العميل")
        self.section_title_changed.emit("تعديل بيانات العميل") # لتغيير عنوان النافذة الرئيسية

        session = next(get_db()) # استخدام الدالة الجديدة للحصول على جلسة
        try:
            # تحميل العميل مع العلاقات المرتبطة (أرقام التواصل والتوكيلات)
            self.client_to_edit = session.query(Client).options(
                joinedload(Client.contact_numbers),
                joinedload(Client.power_of_attorneys) # إذا كنت ستعرضها هنا
            ).get(self.client_id_to_edit)

            if self.client_to_edit:
                # تعبئة الحقول بمعلومات العميل
                self.full_name_input.setText(self.client_to_edit.full_name)
                
                # تعبئة نوع العميل
                client_type_index = self.client_type_combo.findData(self.client_to_edit.client_type)
                if client_type_index != -1:
                    self.client_type_combo.setCurrentIndex(client_type_index)

                # معلومات فردية أو شركة
                if self.client_to_edit.client_type == ClientType.INDIVIDUAL:
                    self.national_id_input.setText(self.client_to_edit.national_id or "")
                    if self.client_to_edit.birth_date:
                        self.birth_date_input.setDate(QDate(self.client_to_edit.birth_date))
                else: # Company or Government Entity
                    self.company_name_input.setText(self.client_to_edit.company_name or "")
                    self.company_registration_number_input.setText(self.client_to_edit.company_registration_number or "")
                    self.company_logo_path_input.setText(self.client_to_edit.company_logo_path or "")
                    self.legal_representative_name_input.setText(self.client_to_edit.legal_representative_name or "")
                    self.legal_representative_title_input.setText(self.client_to_edit.legal_representative_title or "")
                
                self.address_input.setText(self.client_to_edit.address or "")
                self.email_input.setText(self.client_to_edit.email or "")
                self.work_employer_input.setText(self.client_to_edit.work_employer or "")
                self.source_of_contact_input.setText(self.client_to_edit.source_of_contact or "")
                self.notes_input.setText(self.client_to_edit.notes or "")

                # تعبئة أرقام التواصل
                # أولاً، أزل أي حقول أرقام تواصل موجودة افتراضيًا
                for item in reversed(self.contact_number_widgets): # reversed لإزالة العناصر بشكل صحيح
                    self.remove_phone_number_field(item["layout"])
                
                # ثم أضف الأرقام الموجودة في قاعدة البيانات
                if self.client_to_edit.contact_numbers:
                    for contact_num in self.client_to_edit.contact_numbers:
                        self.add_phone_number_field(
                            number=contact_num.number,
                            contact_type_enum=contact_num.contact_type,
                            is_primary=contact_num.is_primary
                        )
                else: # إذا لم يكن هناك أرقام تواصل، أضف حقلاً فارغاً واحداً
                    self.add_phone_number_field()

            else:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على العميل المراد تعديله.")
                self.cancel_requested.emit() # العودة إذا لم يتم العثور على العميل

        except Exception as e:
            QMessageBox.critical(self, "خطأ في التحميل", f"حدث خطأ أثناء تحميل بيانات العميل: {e}")
            print(f"Error loading client for edit: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pass # الجلسة تغلق تلقائيًا

    def save_client(self):
        full_name = self.full_name_input.text().strip()
        if not full_name:
            QMessageBox.warning(self, "إدخال مطلوب", "الرجاء إدخال الاسم الكامل للعميل.")
            return

        client_type = self.client_type_combo.currentData()

        # جمع بيانات العميل بناءً على نوعه
        client_data = {
            "full_name": full_name,
            "client_type": client_type,
            "address": self.address_input.toPlainText().strip(),
            "email": self.email_input.text().strip(),
            "work_employer": self.work_employer_input.text().strip(),
            "source_of_contact": self.source_of_contact_input.text().strip(),
            "notes": self.notes_input.toPlainText().strip(),
        }

        if client_type == ClientType.INDIVIDUAL:
            client_data["national_id"] = self.national_id_input.text().strip()
            client_data["birth_date"] = self.birth_date_input.date().toPyDate() if self.birth_date_input.date() else None
        else: # COMPANY or GOVERNMENT_ENTITY
            client_data["company_name"] = self.company_name_input.text().strip()
            client_data["company_registration_number"] = self.company_registration_number_input.text().strip()
            client_data["company_logo_path"] = self.company_logo_path_input.text().strip()
            client_data["legal_representative_name"] = self.legal_representative_name_input.text().strip()
            client_data["legal_representative_title"] = self.legal_representative_title_input.text().strip()

        session = next(get_db()) # استخدام الدالة الجديدة للحصول على جلسة
        try:
            if self.client_to_edit: # وضع التعديل
                # تحديث بيانات العميل الموجود
                for key, value in client_data.items():
                    setattr(self.client_to_edit, key, value)
                session.add(self.client_to_edit)
                session.flush() # لتحديث ID العميل إذا كان جديداً (لا ينطبق هنا، لكن ممارسة جيدة)
                client_id = self.client_to_edit.id

                # حذف أرقام التواصل القديمة أولاً ثم إضافة الجديدة
                session.query(ClientContactNumber).filter(ClientContactNumber.client_id == client_id).delete(synchronize_session='fetch')
                session.flush() # للتأكد من حذفها قبل إضافة الجديدة
            else: # وضع الإضافة
                new_client = Client(**client_data)
                session.add(new_client)
                session.flush() # للحصول على client_id بعد الإضافة
                client_id = new_client.id

            # حفظ أرقام التواصل
            contact_numbers_to_save = []
            found_primary = False

            for item in self.contact_number_widgets:
                phone_num = item['phone_input'].text().strip()
                contact_type_enum = item['type_combo'].currentData()
                is_primary = item['primary_checkbox'].isChecked()

                if phone_num:
                    # منطق التعامل مع الرقم الأساسي
                    if is_primary:
                        if found_primary:
                            # إذا كان هناك رقم أساسي آخر بالفعل، اجعل هذا الرقم غير أساسي
                            is_primary = False
                        else:
                            found_primary = True # علم أننا وجدنا رقمًا رئيسيًا
                    
                    contact_numbers_to_save.append(ClientContactNumber(
                        client_id=client_id,
                        number=phone_num, # تأكد أن اسم العمود هو 'number'
                        contact_type=contact_type_enum,
                        is_primary=is_primary
                    ))
            
            # إذا لم يتم تحديد أي رقم رئيسي، اجعل أول رقم هو الرئيسي
            if not found_primary and contact_numbers_to_save:
                contact_numbers_to_save[0].is_primary = True

            session.add_all(contact_numbers_to_save)
            
            session.commit()
            QMessageBox.information(self, "نجاح", "تم حفظ بيانات الموكل بنجاح.")
            self.client_saved.emit() # إطلاق الإشارة لتحديث العرض
        except Exception as e:
            session.rollback() # التراجع عن أي تغييرات في حالة الخطأ
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الموكل: {e}")
            print(f"Error saving client: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pass # الجلسة تغلق تلقائيًا

    def close_db_session(self):
        """
        إغلاق جلسة قاعدة البيانات إذا كانت مفتوحة.
        ** لم تعد ضرورية مع استخدام get_db() **
        """
        if self.db_session:
            self.db_session.close()

    def closeEvent(self, event):
        """
        يتم استدعاؤها عند إغلاق النافذة.
        """
        self.close_db_session() # إغلاق الجلسة قبل الإغلاق
        super().closeEvent(event)