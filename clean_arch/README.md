

# Clean Architecture & DDD Project Structure (Flask)

```text
project_root/
├── alembic/                                  # [Stage 5] Database migration scripts
│   ├── versions/                             # Generated revision files
│   ├── env.py                                # Alembic runtime environment configuration
│   └── script.py.mako                        # Migration script template
│
├── src/
│   ├── config/                               # [Stage 0] Bootstrap & Environment Configuration
│   │   ├── __init__.py
│   │   ├── settings.py                       # Environment variables reader (Pydantic Settings)
│   │   └── logging.py                        # Structured logging setup & formatters
│   │
│   ├── domain/                               # [Stage 2] Enterprise Business Rules (Pure Python)
│   │   ├── __init__.py
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── base_entity.py                # Identity-based equality (__eq__, __hash__)
│   │   │   ├── id_factory.py                 # UUID generation utilities
│   │   │   └── domain_event.py               # Base structure for domain events
│   │   ├── value_objects/
│   │   │   ├── __init__.py
│   │   │   └── email.py                      # Immutable value object validated by value
│   │   ├── entities/
│   │   │   ├── __init__.py
│   │   │   └── user.py                       # Aggregate Root (frozen=True, slots=True)
│   │   ├── services/
│   │   │   └── __init__.py                   # Cross-entity domain logic (Domain Services)
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       ├── base_exception.py             # EntityBaseError & DomainValidationError
│   │       ├── entities_validation.py        # EntityValidationError
│   │       └── value_object_validation.py    # ValueObjectValidationError
│   │
│   ├── application/                          # [Stages 3 & 4] Application Business Rules
│   │   ├── __init__.py
│   │   ├── ports/                            # [Stage 3] Abstract Interfaces (typing.Protocol)
│   │   │   ├── __init__.py
│   │   │   ├── uow.py                        # UnitOfWorkProtocol (Transaction boundary)
│   │   │   ├── repositories/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_repository.py        # UserRepositoryProtocol (Aggregate persistence contract)
│   │   │   ├── security/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── password_hasher.py        # PasswordHasherProtocol
│   │   │   │   └── token_provider.py         # TokenProviderProtocol (JWT contract)
│   │   │   └── cache/
│   │   │       ├── __init__.py
│   │   │       └── cache_provider.py         # CacheProtocol
│   │   ├── dtos/                             # [Stage 4] Data Transfer Objects (Pydantic Models)
│   │   │   ├── __init__.py
│   │   │   └── user_dtos.py                  # Input/Output DTOs (includes actor_id for AuthZ)
│   │   ├── use_cases/                        # [Stage 4] Interactors & Business Authorization
│   │   │   ├── __init__.py
│   │   │   └── user/
│   │   │       ├── __init__.py
│   │   │       ├── register_user.py          # Command use case: Create new user
│   │   │       ├── change_user_name.py       # Command use case: Update user name
│   │   │       └── get_user_profile.py       # Query use case: Fetch user details
│   │   └── exceptions/
│   │       ├── __init__.py
│   │       ├── base_exception.py             # ApplicationError base class
│   │       ├── auth_exceptions.py            # UnauthorizedError, ForbiddenActionError
│   │       └── resource_exceptions.py        # ResourceNotFoundError, ResourceConflictError
│   │
│   ├── infrastructure/                       # [Stages 5 & 6] Frameworks, Drivers & Outbound Adapters
│   │   ├── __init__.py
│   │   ├── persistence/                      # [Stage 5] Database & ORM Implementation
│   │   │   ├── __init__.py
│   │   │   ├── database.py                   # SQLAlchemy Engine & sessionmaker factory
│   │   │   ├── uow.py                        # SQLAlchemyUnitOfWork implementation
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py                   # SQLAlchemy DeclarativeBase
│   │   │   │   └── user_model.py             # Mutable ORM table mapping for User
│   │   │   ├── mappers/
│   │   │   │   ├── __init__.py
│   │   │   │   └── user_mapper.py            # Converts between User (Domain) <-> UserModel (ORM)
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── user_repository.py        # SQLAlchemyUserRepository (implements Protocol)
│   │   ├── security/                         # [Stage 6] Concrete Security Implementations
│   │   │   ├── __init__.py
│   │   │   ├── bcrypt_hasher.py              # Implements PasswordHasherProtocol
│   │   │   └── jwt_provider.py               # Implements TokenProviderProtocol
│   │   └── cache/                            # [Stage 6] Concrete Caching Implementations
│   │       ├── __init__.py
│   │       └── redis_cache.py                # Implements CacheProtocol using redis-py
│   │
│   ├── presentation/                         # [Stage 7] Inbound Adapters & Delivery Mechanism (Flask)
│   │   ├── __init__.py
│   │   └── http/
│   │       ├── __init__.py
│   │       ├── controllers/                  # Flask Blueprints / Route Handlers
│   │       │   ├── __init__.py
│   │       │   └── user_controller.py        # HTTP parsing -> DTO -> Use Case -> HTTP JSON Response
│   │       ├── middlewares/
│   │       │   ├── __init__.py
│   │       │   ├── auth_middleware.py        # JWT extraction (AuthN) & RBAC decorators
│   │       │   └── request_logger.py         # Request/Response lifecycle logging & correlation IDs
│   │       └── error_handlers/
│   │           ├── __init__.py
│   │           └── global_handler.py         # Maps Domain/App/Pydantic errors to HTTP status codes
│   │
│   └── bootstrap/                            # [Stage 8] Composition Root & Dependency Injection
│       ├── __init__.py
│       ├── container.py                      # Wires Repositories, UoW, Adapters, and Use Cases
│       ├── app_factory.py                    # Flask create_app() factory
│       └── wsgi.py                           # Gunicorn / uWSGI production entrypoint
│
├── tests/                                    # Cross-Cutting Testing Suite (Mirrors Architecture)
│   ├── __init__.py
│   ├── conftest.py                           # Shared pytest fixtures
│   ├── unit/                                 # Fast, isolated tests (Zero DB / Zero Network)
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   │   └── test_user.py
│   │   │   ├── value_objects/
│   │   │   │   └── test_email.py
│   │   │   └── shared/
│   │   │       └── test_id_factory.py
│   │   └── application/
│   │       ├── fakes/                        # In-memory implementations of Ports
│   │       │   ├── fake_uow.py
│   │       │   └── fake_user_repository.py
│   │       └── use_cases/
│   │           ├── test_register_user.py
│   │           └── test_change_user_name.py
│   ├── integration/                          # Tests Infrastructure adapters against real DB/Redis
│   │   ├── persistence/
│   │   │   ├── test_user_mapper.py
│   │   │   └── test_user_repository.py
│   │   └── cache/
│   │       └── test_redis_cache.py
│   └── e2e/                                  # Full HTTP lifecycle tests via Flask test_client
│       └── http/
│           └── test_user_endpoints.py
│
├── .env.example                              # Template for required environment variables
├── alembic.ini                               # Alembic CLI configuration file
├── docker-compose.yml                        # Local orchestration (App, PostgreSQL, Redis, Nginx)
├── Dockerfile                                # Production container build instructions
├── Makefile                                  # Automation shortcuts (test, lint, migrate, run)
├── pyproject.toml                            # Dependencies, pytest, ruff, and mypy configurations
├── .python-version                            
├── .venv                            
├── uv.lock                            
└── .gitignore                           




