from types import TracebackType
from typing import Protocol

from src.application.protocols.user_repo import UserRepo


class UnitOfWorkProtocol(Protocol):
    user: UserRepo

    def __enter__(self) -> "UnitOfWorkProtocol": ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...

    def commit(
        self,
    ) -> None: ...  # لو معملتش كوممت فانه عند الخروج من السياق هيعمل روول باك تلقائيا
    def rollback(self) -> None: ...
