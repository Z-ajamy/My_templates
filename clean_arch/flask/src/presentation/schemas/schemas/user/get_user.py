from pydantic import BaseModel, EmailStr


# بنعمل كائن لكل جسون حسب النظام و الريست
# في الريست المعرف يكون جزئ من الرابط لذا لا يوجد جسون داخل
class GetUserResponseSchema(BaseModel):
    id: str
    email: EmailStr
    name: str
