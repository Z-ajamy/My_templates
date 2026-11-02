import uuid
from typing import Literal, Self
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    EmailStr,
    UUID4,
    field_validator,
    model_validator,
)

# --- 1. النماذج المتداخلة (Nested Models) ---
class AddressSchema(BaseModel):
    city: str = Field(min_length=2, max_length=50)
    # استخدام التعابير النمطية (Regex) للتحقق من الصيغة
    zip_code: str = Field(pattern=r"^\d{5}$", description="5-digit ZIP code")


# --- 2. النموذج الرئيسي (Main Schema) ---
class UserCreateSchema(BaseModel):
    
    # --- 3. إعدادات الكيان (Model Configuration) ---
    model_config = ConfigDict(
        extra="forbid",             # رفض أي حقول خارجية غير مُعرفة في النموذج (Strictness)
        str_strip_whitespace=True,  # إزالة المسافات البيضاء من أطراف النصوص تلقائياً
        validate_assignment=True,   # إعادة التحقق إذا تم تعديل الحقل بعد إنشاء الكائن (obj.age = 15)
        populate_by_name=True,      # السماح بالتهيئة باستخدام الاسم البرمجي أو الاسم البديل (alias)
    )

    # --- 4. الحقول والقيود (Fields & Constraints) ---
    # استخدام default_factory لتوليد القيمة ديناميكياً، و frozen لمنع تعديلها لاحقاً
    id: UUID4 = Field(default_factory=uuid.uuid4, frozen=True)
    
    # استخدام alias لربط الكيان بواجهة استجابة تستخدم Naming Convention مختلف
    first_name: str = Field(min_length=2, max_length=50, alias="firstName")
    
    email: EmailStr  # يتطلب تثبيت pydantic[email]
    
    # قيود رقمية: ge (أكبر من أو يساوي)، le (أصغر من أو يساوي)
    age: int = Field(ge=18, le=100)
    
    # تقييد القيم المسموحة (Enum alternative)
    role: Literal["admin", "user", "manager"] = Field(default="user")
    
    # حقل اختياري متداخل
    address: AddressSchema | None = None
    
    password: str = Field(min_length=8, repr=False) # repr=False تمنع طباعة الباسورد في الـ Logs
    password_confirm: str = Field(exclude=True)     # exclude=True يمنع ظهور الحقل عند تحويل الكيان إلى JSON

    # --- 5. التحقق المخصص لحقل معين (Field Validator) ---
    # mode="before" يعني التنفيذ قبل التحقق الداخلي الخاص بـ Pydantic
    @field_validator("email", mode="before")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.lower()
        return value

    # --- 6. التحقق المخصص للكيان بالكامل (Model Validator) ---
    # mode="after" يعطيك الكائن (self) بعد أن اجتازت كل الحقول تحققها الفردي
    @model_validator(mode="after")
    def validate_passwords_match_and_role(self) -> Self:
        # 1. التحقق من تطابق كلمات المرور
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
            
        # 2. التحقق المعقد الذي يعتمد على أكثر من حقل (Cross-field validation)
        if self.role == "admin" and self.age < 25:
            raise ValueError("Admin users must be at least 25 years old")
            
        return self


# ==============================================================================
# Usage Examples (أمثلة الاستخدام المعياري):
# ==============================================================================

# 1. التحقق من قاموس (Parsing a Dict - Typical in APIs)
incoming_payload = {
    "firstName": "  Ahmad  ", # سيتم تنظيف المسافات وقبوله بسبب الـ alias
    "email": "AHMAD@Example.com", # سيتم تحويله لحروف صغيرة
    "age": 30,
    "role": "admin",
    "password": "SecurePassword123",
    "password_confirm": "SecurePassword123",
    "address": {"city": "Cairo", "zip_code": "12345"}
}

# التهيئة والتنظيف
user_dto = UserCreateSchema.model_validate(incoming_payload)

# 2. تصدير البيانات (Serialization)
# سيتم استبعاد password_confirm (بسبب exclude=True) وتوليد id تلقائياً
# by_alias=True يضمن خروج البيانات بصيغة firstName وليس first_name
user_dict = user_dto.model_dump(by_alias=True, exclude_none=True)

# 3. التصدير المباشر كـ JSON
user_json_string = user_dto.model_dump_json(by_alias=True)
