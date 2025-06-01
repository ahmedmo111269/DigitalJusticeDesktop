# src/database/models/__init__.py

# استيراد جميع النماذج هنا لتسجيلها في SQLAlchemy's Base
# هذا يضمن أن SQLAlchemy يرى جميع تعريفات الجداول قبل بناء العلاقات.
from .client import Client
from .client_contact_number import ClientContactNumber
from .client_interaction import ClientInteraction
# تأكد من هذا السطر: يجب أن يطابق اسم الكلاس الفعلي في power_of_attorney.py
# بناءً على محادثاتنا الأخيرة، أفضل أن يكون اسم الكلاس هو PowerOfAttorney
# لذا تأكد أن اسم الكلاس في src/database/models/power_of_attorney.py هو class PowerOfAttorney(Base):
from .power_of_attorney import PowerOfAttorney
# إذا كان اسم الكلاس في power_of_attorney.py هو class POA(Base):، فستحتاج إلى تغيير السطر أعلاه إلى:
# from .power_of_attorney import POA
# (لكنني أنصح بتوحيد الاسم إلى PowerOfAttorney ليكون أكثر وضوحاً وتناسقاً)

# إذا كان لديك أي نماذج أخرى (مثل Lawyers, Cases, etc.)، قم باستيرادها هنا أيضاً.
# from .lawyer import Lawyer
# from .case import Case