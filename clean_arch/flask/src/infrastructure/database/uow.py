from types import TracebackType

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from src.application.use_cases.exceptions import (
    ConcurrentModificationError,
    ResourceConflictError,
)
from src.infrastructure.database.repositories.user_repo import UserRepo


class SqlAlchemyUnitOfWork:
    def __init__(self, session_maker: sessionmaker[Session]) -> None:
        self._sessmkr = session_maker
        self.session: Session

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._sessmkr()
        self.user = UserRepo(session=self.session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.session.rollback()
        self.session.close()

    # لو معملتش كوممت فانه عند الخروج من السياق هيعمل روول باك تلقائيا

    def commit(
        self,
    ) -> None:
        try:
            self.session.commit()
        except StaleDataError as e:
            self.rollback()
            raise ConcurrentModificationError(
                resource_name="Database_Record",
                reason="Optimistic lock failed during commit",
            ) from e

        except IntegrityError as e:
            self.rollback()
            raise ResourceConflictError(
                resource_name="Database_Record",
                reason="Database constraint violated (e.g., duplicate email)",
            ) from e

    def rollback(self) -> None:
        self.session.rollback()
