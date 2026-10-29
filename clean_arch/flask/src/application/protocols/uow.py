from typing import Protocol, Any

from src.application.protocols.user_repo import UserRepoProtocole

class UnitOfWorkProtocol(Protocol):
    user: UserRepoProtocole

    def __enter__(self) -> "UnitOfWorkProtocol": ...
    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None: ...

    def commit(self) -> None: ...
    def rollback(self) -> None: ...

        

