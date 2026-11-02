from src.domain.entities.user import User
from src.domain.shared.value_objs import Email

a = User(id="1", name="Ali", email=Email(value="a4@gmail.com"))
b = User(id="1", name="bi", email=Email(value="a4@gmail.com"))

print(a == b)
