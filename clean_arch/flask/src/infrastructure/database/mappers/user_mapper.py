from src.domain.entities.user import User
from src.domain.shared.value_objs import Email
from src.infrastructure.database.sqlalchemy_models.user import UserORM


class UserMapper:
    @staticmethod
    def to_orm(duser: User | None) -> UserORM | None:
        if not duser:
            return None
        orm_obj = UserORM(
            id=duser.id,
            name=duser.name,
            email=duser.email.value,
            version_id=duser.version,
        )
        return orm_obj

    @staticmethod
    def to_domain(ouser: UserORM | None) -> User | None:
        if not ouser:
            return None
        email = Email(value=ouser.email)

        domain_user = User(
            id=ouser.id, name=ouser.name, email=email, version=ouser.version_id
        )
        return domain_user
