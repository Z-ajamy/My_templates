from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.domain.entities.user import User
from src.domain.shared.value_objs import Email
from src.infrastructure.database.mappers.user_mapper import UserMapper
from src.infrastructure.database.sqlalchemy_models.user import UserORM


class UserRepo:
    def __init__(self, session: Session):
        self.session = session

    def save(self, user: User) -> None:  # save and update the object
        stmt = select(UserORM).where(UserORM.id == user.id)
        orm_user = self.session.execute(stmt).scalar_one_or_none()

        if orm_user:
            orm_user.name = user.name
            orm_user.email = user.email.value
        else:
            new_orm_user = UserMapper.to_orm(user)
            self.session.add(new_orm_user)

    def remove(self, user: User) -> None:
        stmt = delete(UserORM).where(UserORM.id == user.id)
        self.session.execute(stmt)

    def get_by_id(self, id: str, with_for_update: bool = False) -> User | None:
        stmt = select(UserORM).where(UserORM.id == id)
        if with_for_update:
            stmt = stmt.with_for_update()
        orm_user = self.session.execute(stmt).scalar_one_or_none()
        if not orm_user:
            return None

        domain_user = UserMapper.to_domain(orm_user)
        return domain_user

    def get_by_email(self, email: Email, with_for_update: bool = False) -> User | None:
        stmt = select(UserORM).where(UserORM.email == email.value)
        if with_for_update:
            stmt = stmt.with_for_update()
        orm_user = self.session.execute(stmt).scalar_one_or_none()
        if not orm_user:
            return None

        domain_user = UserMapper.to_domain(orm_user)
        return domain_user


# هااااااااااااام
# execute هي تجاهل تام لكل قواعد ال sqlalchemy  هي تطلق الجمل مباشرة ولا تكترث للقواعد النظامية مثل mapper_args
