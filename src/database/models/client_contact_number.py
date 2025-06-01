# src/database/models/client_contact_number.py

from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum, Boolean # أضف Boolean هنا
from sqlalchemy.orm import relationship
from database.db import Base
import enum

# تعريف أنواع أرقام التواصل
class ContactType(enum.Enum):
    PHONE = "هاتف"
    MOBILE = "جوال"
    FAX = "فاكس"
    WHATSAPP = "واتساب"
    OTHER = "أخرى"

class ClientContactNumber(Base):
    __tablename__ = "client_contact_numbers"
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    number = Column(String(50), nullable=False)
    contact_type = Column(SQLEnum(ContactType), default=ContactType.MOBILE, nullable=False)
    notes = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False, nullable=False) # **تم إضافة هذا السطر**

    client = relationship("Client", back_populates="contact_numbers")

    def __repr__(self):
        return f"<ClientContactNumber(id={self.id}, client_id={self.client_id}, number='{self.number}')>"