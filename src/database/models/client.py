# src/database/models/client.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# لا حاجة لاستيراد datetime هنا إذا كنا نستخدم func.now() لـ created_at و updated_at
# ويمكن استيرادها عند الحاجة لدوال معينة مثل datetime.now() لـ interaction_date في client_interaction.py
# from datetime import datetime
import enum

from database.db import Base # تأكد من أن هذا السطر موجود

# تعريفات الـ Enums لتنظيم البيانات - يجب أن تكون هنا فقط الـ Enums الخاصة بالـ Client
class ClientType(enum.Enum):
    INDIVIDUAL = "فرد"
    COMPANY = "شركة/مؤسسة"
    GOVERNMENT_ENTITY = "جهة حكومية"

# تعريفات Enums الأخرى مثل ContactType و InteractionType
# يجب أن تكون في ملفاتها الخاصة (client_contact_number.py و client_interaction.py)
# ولن يتم تكرارها هنا.

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    # معلومات أساسية
    full_name = Column(String(255), nullable=False, index=True)
    client_type = Column(SQLEnum(ClientType), default=ClientType.INDIVIDUAL, nullable=False)
    
    # معلومات للأفراد
    national_id = Column(String(50), unique=True, nullable=True) # الرقم القومي (يمكن أن يكون فارغاً للشركات)
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(10), nullable=True) # ذكر/أنثى
    nationality = Column(String(50), nullable=True)
    marital_status = Column(String(20), nullable=True) # أعزب/متزوج/مطلق/أرمل
    profession = Column(String(100), nullable=True) # المهنة
    
    # معلومات للشركات/الجهات
    commercial_registration_no = Column(String(100), unique=True, nullable=True) # رقم السجل التجاري/الضريبي
    company_logo_path = Column(String(255), nullable=True) # مسار شعار الشركة
    legal_representative_name = Column(String(255), nullable=True) # اسم الممثل القانوني
    legal_representative_title = Column(String(100), nullable=True) # صفة الممثل

    # معلومات الاتصال
    address = Column(Text, nullable=True)
    email = Column(String(255), nullable=True) # بريد إلكتروني رئيسي
    
    # معلومات إضافية
    work_employer = Column(String(255), nullable=True) # جهة العمل
    source_of_contact = Column(String(100), nullable=True) # كيف عرف المكتب بالموكل
    notes = Column(Text, nullable=True) # ملاحظات إضافية

    # بيانات النظام
    is_hidden = Column(Boolean, default=False, nullable=False) # لإخفاء الموكل عن العرض العام
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), default=func.now())

    # العلاقات
    # عند تعريف العلاقات بين النماذج، استخدم اسم النموذج كنص لتجنب الاستيراد الدائري.
    # SQLAlchemy ستقوم بحل هذا الاسم لاحقاً بمجرد تعريف جميع النماذج.
    power_of_attorneys = relationship("PowerOfAttorney", back_populates="client")
    contact_numbers = relationship("ClientContactNumber", back_populates="client", cascade="all, delete-orphan")
    interactions = relationship("ClientInteraction", back_populates="client")

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.full_name}', type='{self.client_type.value}')>"

# تم نقل تعريف ClientContactNumber و ClientInteraction إلى ملفاتهما الخاصة.