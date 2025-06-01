# src/gui/add_client_form.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QTextEdit, QDateEdit, QScrollArea, QFrame, QMessageBox,
    QCheckBox, QGroupBox, QSpacerItem, QSizePolicy, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate, QSize # تأكد من وجود QSize
from PyQt5.QtGui import QIcon, QFont # تأكد من وجود QFont

from gui.style import PRIMARY_COLOR, BACKGROUND_COLOR, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR, DANGER_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, WARNING_COLOR, CARD_BACKGROUND_COLOR

from database.db import SessionLocal
from database.models.client import Client, ClientType
from database.models.client_contact_number import ClientContactNumber, ContactType
from datetime import datetime

from sqlalchemy.orm import relationship, joinedload # <--- هذا السطر هو الأهم! يجب أن يكون موجوداً ويحتوي على relationship و joinedload

class AddClientForm(QWidget):
    client_saved = pyqtSignal()
    cancel_requested = pyqtSignal()

    def __init__(self, client_id_to_edit=None, parent=None):
        super().__init__(parent)
        self.db_session = SessionLocal()
        self.client_id_to_edit = client_id_to_edit
        self.client_to_edit = None
        self.contact_number_widgets = []
        
        self.setup_ui()

        if self.client_id_to_edit:
            self.load_client_data_for_edit()
            self.setWindowTitle("تعديل بيانات موكل")
        else:
            self.setWindowTitle("إضافة موكل جديد")
            self.add_phone_number_field(is_primary_default=True)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(20)

        # عنوان النموذج
        self.form_title = QLabel("إضافة موكل جديد")
        self.form_title.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {PRIMARY_COLOR};")
        self.form_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.form_title)

        # منطقة المحتوى القابلة للتمرير (إذا كان النموذج طويلاً)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout(self.scroll_content)
        self.scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_content_layout.setSpacing(15)
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        # مجموعة معلومات الموكل الأساسية
        self._create_basic_info_group()
        self.scroll_content_layout.addWidget(self.basic_info_group)

        # مجموعة معلومات الاتصال
        self._create_contact_info_group()
        self.scroll_content_layout.addWidget(self.contact_info_group)
        
        # ملاحظات إضافية
        self._create_notes_group()
        self.scroll_content_layout.addWidget(self.notes_group)

        # أزرار الحفظ والإلغاء
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch(1) # لدفع الأزرار لليمين

        self.save_button = QPushButton("حفظ الموكل")
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {ACCENT_COLOR};
                color: white;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #218838;
            }}
        """)
        self.save_button.clicked.connect(self.save_client)
        self.buttons_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {DANGER_COLOR};
                color: white;
                border-radius: 8px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #c82333;
            }}
        """)
        self.cancel_button.clicked.connect(self.cancel_requested.emit)
        self.buttons_layout.addWidget(self.cancel_button)

        self.main_layout.addLayout(self.buttons_layout)
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {BACKGROUND_COLOR};
                color: {TEXT_COLOR};
                font-family: 'Arial';
            }}
            QLabel {{
                font-size: 14px;
                font-weight: bold;
            }}
            QLineEdit, QTextEdit, QComboBox, QDateEdit {{
                padding: 10px;
                border: 1px solid {BORDER_COLOR};
                border-radius: 5px;
                background-color: {CARD_BACKGROUND_COLOR};
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {{
                border: 1px solid {PRIMARY_COLOR};
            }}
            QComboBox::drop-down {{
                border: 0px;
            }}
            QComboBox::down-arrow {{
                image: url(assets/icons/down_arrow.png); /* تأكد من المسار الصحيح للأيقونة */
                width: 16px;
                height: 16px;
            }}
            QGroupBox {{
                font-size: 18px;
                font-weight: bold;
                color: {PRIMARY_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 20px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: {BACKGROUND_COLOR};
            }}
            QScrollArea {{
                border: none;
            }}
        """)
    
    def _create_basic_info_group(self):
        self.basic_info_group = QGroupBox("المعلومات الأساسية")
        basic_layout = QGridLayout(self.basic_info_group)
        basic_layout.setSpacing(10)

        # الصف الأول: الاسم الكامل، نوع الموكل
        basic_layout.addWidget(QLabel("الاسم الكامل:"), 0, 0)
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("أدخل الاسم الكامل")
        basic_layout.addWidget(self.full_name_input, 0, 1)

        basic_layout.addWidget(QLabel("نوع الموكل:"), 0, 2)
        self.client_type_combo = QComboBox()
        for client_type in ClientType:
            self.client_type_combo.addItem(client_type.value, client_type) # القيمة المرئية, القيمة الحقيقية (Enum)
        self.client_type_combo.currentIndexChanged.connect(self.toggle_client_type_fields)
        basic_layout.addWidget(self.client_type_combo, 0, 3)

        # الصف الثاني: الرقم القومي، تاريخ الميلاد (للفرد) / رقم السجل التجاري (للشركة)
        basic_layout.addWidget(QLabel("الرقم القومي:"), 1, 0)
        self.national_id_input = QLineEdit()
        self.national_id_input.setPlaceholderText("أدخل الرقم القومي")
        basic_layout.addWidget(self.national_id_input, 1, 1)

        basic_layout.addWidget(QLabel("تاريخ الميلاد:"), 1, 2)
        self.date_of_birth_input = QDateEdit(calendarPopup=True)
        self.date_of_birth_input.setDisplayFormat("yyyy-MM-dd")
        self.date_of_birth_input.setDate(QDate.currentDate()) # تاريخ اليوم افتراضياً
        basic_layout.addWidget(self.date_of_birth_input, 1, 3)

        # حقول معلومات الشركة (مخفية افتراضياً)
        self.company_fields_group = QGroupBox("معلومات الشركة/المؤسسة")
        self.company_fields_group.setStyleSheet("QGroupBox { background-color: #f0f0f0; border: 1px solid #ddd; border-radius: 5px; padding-top: 15px;} QGroupBox::title { color: #555; }")
        company_layout = QGridLayout(self.company_fields_group)
        company_layout.setSpacing(10)

        company_layout.addWidget(QLabel("رقم السجل التجاري/الضريبي:"), 0, 0)
        self.commercial_reg_no_input = QLineEdit()
        company_layout.addWidget(self.commercial_reg_no_input, 0, 1)

        company_layout.addWidget(QLabel("اسم الممثل القانوني:"), 1, 0)
        self.legal_rep_name_input = QLineEdit()
        company_layout.addWidget(self.legal_rep_name_input, 1, 1)

        company_layout.addWidget(QLabel("صفة الممثل:"), 2, 0)
        self.legal_rep_title_input = QLineEdit()
        company_layout.addWidget(self.legal_rep_title_input, 2, 1)

        company_layout.setColumnStretch(1, 1) # جعل حقول الإدخال تتمدد
        basic_layout.addWidget(self.company_fields_group, 2, 0, 1, 4) # تمتد على 4 أعمدة

        # يجب أن تكون مخفية في البداية
        self.toggle_client_type_fields()

    def _create_contact_info_group(self):
        self.contact_info_group = QGroupBox("معلومات الاتصال")
        contact_layout = QVBoxLayout(self.contact_info_group)
        contact_layout.setSpacing(10)

        # البريد الإلكتروني
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("البريد الإلكتروني:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@domain.com")
        email_layout.addWidget(self.email_input)
        contact_layout.addLayout(email_layout)

        # العنوان
        address_layout = QHBoxLayout()
        address_layout.addWidget(QLabel("العنوان:"))
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("العنوان التفصيلي للموكل")
        address_layout.addWidget(self.address_input)
        contact_layout.addLayout(address_layout)

        # قسم أرقام الهواتف (ديناميكي)
        self.phone_numbers_layout = QVBoxLayout()
        contact_layout.addLayout(self.phone_numbers_layout)
        
        add_phone_button = QPushButton("إضافة رقم هاتف آخر")
        add_phone_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {SECONDARY_COLOR};
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #5a6268;
            }}
        """)
        add_phone_button.clicked.connect(self.add_phone_number_field)
        contact_layout.addWidget(add_phone_button, alignment=Qt.AlignmentFlag.AlignRight)

    def _create_notes_group(self):
        self.notes_group = QGroupBox("ملاحظات إضافية")
        notes_layout = QVBoxLayout(self.notes_group)
        notes_layout.setSpacing(10)
        
        self.notes_text_edit = QTextEdit()
        self.notes_text_edit.setPlaceholderText("أدخل أي ملاحظات إضافية عن الموكل...")
        self.notes_text_edit.setMinimumHeight(100)
        notes_layout.addWidget(self.notes_text_edit)

    def add_phone_number_field(self, phone_number="", contact_type_enum=ContactType.MOBILE, is_primary=False, is_primary_default=False):
        phone_row_widget = QWidget()
        phone_row_layout = QHBoxLayout(phone_row_widget)
        phone_row_layout.setContentsMargins(0, 0, 0, 0)
        phone_row_layout.setSpacing(10)

        # حقل إدخال الرقم
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("رقم الهاتف")
        phone_input.setText(phone_number)
        phone_row_layout.addWidget(phone_input)

        # نوع الاتصال (Mobile, Landline, etc.)
        type_combo = QComboBox()
        for c_type in ContactType:
            type_combo.addItem(c_type.value, c_type)
        
        if contact_type_enum:
            index = type_combo.findData(contact_type_enum)
            if index != -1:
                type_combo.setCurrentIndex(index)
        
        phone_row_layout.addWidget(type_combo)

        # تحديد كـ رئيسي
        primary_checkbox = QCheckBox("رقم رئيسي")
        primary_checkbox.setChecked(is_primary or is_primary_default)
        primary_checkbox.stateChanged.connect(lambda state, cb=primary_checkbox: self.handle_primary_checkbox_state(state, cb))
        phone_row_layout.addWidget(primary_checkbox)

        # زر الحذف
        remove_button = QPushButton(QIcon('assets/icons/delete_icon.png'), "") # تأكد من المسار
        remove_button.setFixedSize(30, 30)
        remove_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: rgba(220, 53, 69, 0.2);
                border-radius: 5px;
            }}
        """)
        remove_button.clicked.connect(lambda: self.remove_phone_number_field(phone_row_widget))
        phone_row_layout.addWidget(remove_button)

        self.phone_numbers_layout.addWidget(phone_row_widget)
        self.contact_number_widgets.append({
            'widget': phone_row_widget,
            'phone_input': phone_input,
            'type_combo': type_combo,
            'primary_checkbox': primary_checkbox
        })
        
        if is_primary_default:
            self.handle_primary_checkbox_state(Qt.CheckState.Checked, primary_checkbox)


    def remove_phone_number_field(self, widget_to_remove):
        self.phone_numbers_layout.removeWidget(widget_to_remove)
        for item in self.contact_number_widgets:
            if item['widget'] == widget_to_remove:
                self.contact_number_widgets.remove(item)
                break
        widget_to_remove.deleteLater()

        if not any(w['primary_checkbox'].isChecked() for w in self.contact_number_widgets) and self.contact_number_widgets:
            self.contact_number_widgets[0]['primary_checkbox'].setChecked(True)

    def handle_primary_checkbox_state(self, state, current_checkbox):
        if state == Qt.CheckState.Checked:
            for item in self.contact_number_widgets:
                if item['primary_checkbox'] != current_checkbox:
                    item['primary_checkbox'].setChecked(False)

    def toggle_client_type_fields(self):
        selected_type = self.client_type_combo.currentData()

        self.national_id_input.setVisible(selected_type == ClientType.INDIVIDUAL)
        self.date_of_birth_input.setVisible(selected_type == ClientType.INDIVIDUAL)
        
        national_id_label = self.basic_info_group.layout().itemAtPosition(1, 0).widget()
        date_of_birth_label = self.basic_info_group.layout().itemAtPosition(1, 2).widget()
        
        if national_id_label: national_id_label.setVisible(selected_type == ClientType.INDIVIDUAL)
        if date_of_birth_label: date_of_birth_label.setVisible(selected_type == ClientType.INDIVIDUAL)
        
        self.company_fields_group.setVisible(selected_type != ClientType.INDIVIDUAL)


    def load_client_data_for_edit(self):
        self.close_db_session()
        self.db_session = SessionLocal()

        # <--- التصحيح هنا: استخدام joinedload بدلاً من relationship
        self.client_to_edit = self.db_session.query(Client).options(
            joinedload(Client.contact_numbers) 
        ).get(self.client_id_to_edit)

        if not self.client_to_edit:
            QMessageBox.critical(self, "خطأ", "لم يتم العثور على الموكل المطلوب للتعديل.")
            self.cancel_requested.emit()
            print("لا يوجد موكل للتعديل بعد البحث في قاعدة البيانات.")
            return

        print(f"بدء تحميل بيانات الموكل للتعديل: {self.client_to_edit.full_name}")

        try:
            self.form_title.setText(f"تعديل بيانات الموكل: {self.client_to_edit.full_name}")

            self.full_name_input.setText(self.client_to_edit.full_name)
            # Find index by data (enum value)
            index = self.client_type_combo.findData(self.client_to_edit.client_type)
            if index != -1:
                self.client_type_combo.setCurrentIndex(index)
            
            self.toggle_client_type_fields()

            if self.client_to_edit.client_type == ClientType.INDIVIDUAL:
                self.national_id_input.setText(self.client_to_edit.national_id or "")
                if self.client_to_edit.date_of_birth:
                    if isinstance(self.client_to_edit.date_of_birth, (datetime, datetime.date)):
                        qdate = QDate(self.client_to_edit.date_of_birth.year, self.client_to_edit.date_of_birth.month, self.client_to_edit.date_of_birth.day)
                        self.date_of_birth_input.setDate(qdate)
                    else: 
                        try:
                            date_obj = datetime.strptime(str(self.client_to_edit.date_of_birth), "%Y-%m-%d").date()
                            qdate = QDate(date_obj.year, date_obj.month, date_obj.day)
                            self.date_of_birth_input.setDate(qdate)
                        except ValueError:
                            print(f"تحذير: لا يمكن تحويل تاريخ الميلاد '{self.client_to_edit.date_of_birth}' إلى تاريخ صالح.")
                            self.date_of_birth_input.clear()
            else: 
                self.commercial_reg_no_input.setText(self.client_to_edit.commercial_registration_no or "")
                self.legal_rep_name_input.setText(self.client_to_edit.legal_representative_name or "")
                self.legal_rep_title_input.setText(self.client_to_edit.legal_representative_title or "")
                        
            self.address_input.setText(self.client_to_edit.address or "")
            self.email_input.setText(self.client_to_edit.email or "")
            self.notes_text_edit.setText(self.client_to_edit.notes or "")

            for widget_info in list(self.contact_number_widgets): 
                self.remove_phone_number_field(widget_info['widget'])
            self.contact_number_widgets = [] 

            if self.client_to_edit.contact_numbers:
                for contact in self.client_to_edit.contact_numbers:
                    self.add_phone_number_field(
                        phone_number=contact.number, 
                        contact_type_enum=contact.contact_type, 
                        is_primary=getattr(contact, 'is_primary', False) 
                    )
            else:
                self.add_phone_number_field(is_primary_default=True)
            
            print("تم تحميل بيانات الموكل بنجاح.")

        except Exception as e:
            print(f"-------------------- خطأ في load_client_data_for_edit! --------------------")
            print(f"نوع الخطأ: {type(e).__name__}")
            print(f"القيمة: {e}")
            import traceback
            traceback.print_exc()
            print(f"----------------------------------------------------------")
            QMessageBox.critical(self, "خطأ في التحميل", f"حدث خطأ أثناء تحميل بيانات الموكل: {e}")
            self.cancel_requested.emit()

    def save_client(self):
        full_name = self.full_name_input.text().strip()
        client_type = self.client_type_combo.currentData()
        email = self.email_input.text().strip()
        address = self.address_input.text().strip()
        notes = self.notes_text_edit.toPlainText().strip()

        if not full_name:
            QMessageBox.warning(self, "خطأ في الإدخال", "الرجاء إدخال الاسم الكامل للموكل.")
            return

        national_id = None
        date_of_birth = None
        commercial_reg_no = None
        legal_rep_name = None
        legal_rep_title = None

        if client_type == ClientType.INDIVIDUAL:
            national_id = self.national_id_input.text().strip()
            date_of_birth_qdate = self.date_of_birth_input.date()
            date_of_birth = date_of_birth_qdate.toPyDate() if date_of_birth_qdate.isValid() else None
            
            if national_id: 
                existing_client = self.db_session.query(Client).filter_by(national_id=national_id).first()
                if existing_client:
                    if self.client_to_edit and existing_client.id == self.client_to_edit.id:
                        pass
                    else:
                        QMessageBox.warning(self, "خطأ في الإدخال", "الرقم القومي المدخل مسجل بالفعل لموكل آخر. الرجاء إدخال رقم قومي فريد.")
                        return

        else: 
            commercial_reg_no = self.commercial_reg_no_input.text().strip()
            legal_rep_name = self.legal_rep_name_input.text().strip()
            legal_rep_title = self.legal_rep_title_input.text().strip()

            if commercial_reg_no:
                existing_company = self.db_session.query(Client).filter_by(commercial_registration_no=commercial_reg_no).first()
                if existing_company:
                    if self.client_to_edit and existing_company.id == self.client_to_edit.id:
                        pass
                    else:
                        QMessageBox.warning(self, "خطأ في الإدخال", "رقم السجل التجاري/الضريبي مسجل بالفعل لموكل آخر. الرجاء إدخال رقم فريد.")
                        return

        try:
            if self.client_to_edit:
                client_instance = self.client_to_edit
                if client_instance:
                    client_instance.full_name = full_name
                    client_instance.client_type = client_type
                    client_instance.email = email if email else None
                    client_instance.address = address if address else None
                    client_instance.notes = notes if notes else None

                    if client_type == ClientType.INDIVIDUAL:
                        client_instance.national_id = national_id
                        client_instance.date_of_birth = date_of_birth
                        client_instance.commercial_registration_no = None
                        client_instance.legal_representative_name = None
                        client_instance.legal_representative_title = None
                    else:
                        client_instance.commercial_registration_no = commercial_reg_no
                        client_instance.legal_representative_name = legal_rep_name
                        client_instance.legal_representative_title = legal_rep_title
                        client_instance.national_id = None
                        client_instance.date_of_birth = None

                    self.db_session.add(client_instance)
                    client_id = client_instance.id

                    self.db_session.query(ClientContactNumber).filter_by(client_id=client_id).delete()
                    self.db_session.flush()

            else: 
                new_client = Client(
                    full_name=full_name,
                    client_type=client_type,
                    national_id=national_id,
                    date_of_birth=date_of_birth,
                    commercial_registration_no=commercial_reg_no,
                    legal_representative_name=legal_rep_name,
                    legal_representative_title=legal_rep_title,
                    address=address,
                    email=email,
                    notes=notes
                )
                self.db_session.add(new_client)
                self.db_session.flush()
                client_id = new_client.id

            found_primary = False
            contact_numbers_to_save = []
            for item in self.contact_number_widgets:
                phone_num = item['phone_input'].text().strip()
                contact_type_enum = item['type_combo'].currentData()
                is_primary = item['primary_checkbox'].isChecked()

                if phone_num:
                    if is_primary:
                        if found_primary:
                            is_primary = False
                        else:
                            found_primary = True
                    
                    contact_numbers_to_save.append(ClientContactNumber(
                        client_id=client_id,
                        number=phone_num, 
                        contact_type=contact_type_enum,
                        is_primary=is_primary
                    ))
            
            if not found_primary and contact_numbers_to_save:
                contact_numbers_to_save[0].is_primary = True

            self.db_session.add_all(contact_numbers_to_save)
            
            self.db_session.commit()
            QMessageBox.information(self, "نجاح", "تم حفظ بيانات الموكل بنجاح.")
            self.client_saved.emit()
        except Exception as e:
            self.db_session.rollback()
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الموكل: {e}")
            print(f"Error saving client: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.close_db_session()

    def close_db_session(self):
        if self.db_session:
            self.db_session.close()

    def closeEvent(self, event):
        self.close_db_session()
        super().closeEvent(event)