from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.database.uow import SqlAlchemyUnitOfWork
from src.application.use_cases.user.create_user.create_user_use_case import CreateUserUseCase
from src.application.use_cases.user.get_user.get_user_use_case import GetUserUseCase
from src.application.use_cases.user.update_email.update_email_use_case import UpdateEmailUseCase

class AppContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    engine = providers.Singleton(
        create_engine,
        config.db_url,
        echo=False,
        connect_args={"check_same_thread": False} if config.db_url().startswith("sqlite") else {}
    )

    session_maker = providers.Singleton(
        sessionmaker,
        bind=engine,
        autoflush=False,
        autocommit=False
    )

    uow = providers.Factory(
        SqlAlchemyUnitOfWork,
        session_maker=session_maker
    )

    get_user_use_case = providers.Factory(
        GetUserUseCase,
        uow=uow
    )
    
    update_email_use_case = providers.Factory(
        UpdateEmailUseCase,
        uow=uow
    )

    create_user_use_case = providers.Factory(
        CreateUserUseCase,
        uow=uow
    )
    
    get_user_use_case = providers.Factory(
        GetUserUseCase,
        uow=uow
    )
