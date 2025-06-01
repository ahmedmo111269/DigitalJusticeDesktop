# src/database/models/__init__.py

# استيراد جميع النماذج هنا لتسجيلها في SQLAlchemy's Base
# هذا يضمن أن SQLAlchemy يرى جميع تعريفات الجداول قبل بناء العلاقات.
from .client import Client
from .client_contact_number import ClientContactNumber, ContactType # تأكد من استيراد ContactType هنا أيضاً
from .client_interaction import ClientInteraction
from .power_of_attorney import PowerOfAttorney, PowerOfAttorneyType, PowerOfAttorneyStatus # استيراد كل الكلاسات المتعلقة

# إذا كان لديك أي نماذج أخرى (مثل Lawyers, Cases, etc.)، قم باستيرادها هنا أيضاً.
# from .lawyer import Lawyer
# from .case import Case