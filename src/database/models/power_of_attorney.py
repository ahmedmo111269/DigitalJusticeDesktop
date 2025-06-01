# src/database/models/power_of_attorney.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime # لإعداد default values في الأعمدة

from database.db import Base # تأكد من أن هذا السطر موجود

# تعريفات Enums
class PowerOfAttorneyStatus(enum.Enum):
    ACTIVE = "نشط"
    EXPIRED = "منتهي الصلاحية"
    ARCHIVED = "مؤرشف"
    REVOKED = "ملغي" # إذا تم إلغاؤه يدوياً

class PowerOfAttorneyType(enum.Enum):
    GENERAL = "عام"
    SPECIFIC = "خاص"
    ADMINISTRATIVE = "إداري"
    JUDICIAL = "قضائي"
    BANKING = "بنكي"
    SALE = "بيع"
    MARRIAGE = "زواج"
    DIVORCE = "طلاق"
    OTHER = "أخرى"

class PowerOfAttorney(Base):
    __tablename__ = "power_of_attorneys"
    # هذا الخيار مفيد إذا كنت تقوم بتحديث النموذج وتواجه أخطاء عند إعادة تشغيل التطبيق
    # __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    
    # ربط الموكل بالتوكيل (علاقة One-to-Many)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    
    power_of_attorney_number = Column(String(100), unique=True, nullable=False, index=True) # رقم التوكيل
    power_of_attorney_type = Column(SQLEnum(PowerOfAttorneyType), nullable=False) # نوع التوكيل (عام، خاص، إلخ)
    issue_date = Column(DateTime, nullable=False) # تاريخ إصدار التوكيل
    expiry_date = Column(DateTime, nullable=True) # تاريخ انتهاء صلاحية التوكيل
    status = Column(SQLEnum(PowerOfAttorneyStatus), default=PowerOfAttorneyStatus.ACTIVE, nullable=False) # حالة التوكيل
    notes = Column(Text, nullable=True) # ملاحظات إضافية

    # بيانات النظام
    is_hidden = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), default=func.now())

    # العلاقات
    # العلاقة مع الموكل (Client)
    client = relationship("Client", back_populates="power_of_attorneys")

    # يمكن إضافة علاقات أخرى هنا لاحقاً، مثل:
    # علاقة التوكيل بالقضايا (One-to-Many من منظور التوكيل)
    # cases = relationship("CasePowerOfAttorney", back_populates="power_of_attorney")
    
    def __repr__(self):
        # تصحيح اسم العمود: PowerOfAttorney_number إلى power_of_attorney_number
        return f"<PowerOfAttorney(id={self.id}, number='{self.power_of_attorney_number}', client_id={self.client_id})>"