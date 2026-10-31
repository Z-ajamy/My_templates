from typing import Protocol

from src.domain.entities.user import User
from src.domain.shared.value_objs import Email


class UserRepo(Protocol):
    # Commands --Does change the data--
    def save(self, user: User) -> None: ...
    def remove(self, user: User) -> None: ...

    # التخزين في نمط المستودع يجب ان يحاكي التخزين في الرام "تجريد مطلق"
    # لا نحتاج لعمل update كدالة هنا لان ال sqlalcheme Dirty Checking موجود و هيدير تلك العملية تلقائيابمجرد اضافة الuser للجلسة

    # Queries --Does not change the data--
    # Optimistic Locking is defult and Pessimistic Locking is optional
    def get_by_id(self, id: str, with_for_update: bool = False) -> User | None: ...
    def get_by_email(
        self, email: Email, with_for_update: bool = False
    ) -> User | None: ...
