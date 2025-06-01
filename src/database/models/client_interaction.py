# src/database/models/client_interaction.py

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import enum

class InteractionType(enum.Enum):
    CALL = "مكالمة هاتفية"
    MEETING = "اجتماع"
    EMAIL = "بريد إلكتروني"
    WHATSAPP = "واتساب"
    VISIT = "زيارة"
    OTHER = "أخرى"

class ClientInteraction(Base):
    __tablename__ = "client_interactions"
    # أضف هذا السطر لتجنب مشكلة التعريف المتكرر للجدول
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    interaction_type = Column(SQLEnum(InteractionType), default=InteractionType.CALL, nullable=False)
    interaction_date = Column(DateTime, default=func.now(), nullable=False)
    summary = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)

    # بيانات النظام
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), default=func.now())

    # العلاقة العكسية مع Client (باستخدام الاسم كنص لتجنب الاستيراد الدائري)
    client = relationship("Client", back_populates="interactions")

    def __repr__(self):
        return f"<ClientInteraction(id={self.id}, client_id={self.client_id}, type='{self.interaction_type.value}')>"