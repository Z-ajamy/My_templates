import sys
import asyncio
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Table, Column, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 1. Base Class
class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # lazy="selectin": CRITICAL FOR ASYNC. Emits a second SELECT statement immediately to load the collection.
    # Prevents MissingGreenletError when accessing author.books outside of an active awaitable query.
    books: Mapped[List["Book"]] = relationship(
        back_populates="author", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Book(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    
    author: Mapped["Author"] = relationship(back_populates="books", lazy="selectin")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <async_database_url>")
        # Example for async DB URLs:
        # PostgreSQL: postgresql+asyncpg://user:pass@host/db
        # MySQL: mysql+asyncmy://user:pass@host/db (or aiomysql)
        # SQLite: sqlite+aiosqlite:///file.db
        sys.exit(1)
        
    db_url = sys.argv[1]

    # create_async_engine(): The core of asynchronous execution in SQLAlchemy.
    # pool_pre_ping=True: Tests connections before handing them out.
    # pool_size=10, max_overflow=20: Concurrency limits. Tune based on async workers (e.g., Uvicorn workers).
    engine = create_async_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,       
        max_overflow=20     
    )
    
    # Async table creation requires run_sync because DDL operations don't have native async equivalents.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # async_sessionmaker(): Factory for AsyncSession.
    # expire_on_commit=False: Prevents detaching objects post-commit. Mandatory in async contexts if objects are accessed later.
    AsyncSessionLocal = async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    session = AsyncSessionLocal()

    try:
        author1 = Author(name="Nagib Mahfouz")
        book1 = Book(title="Children of the Alley")
        book2 = Book(title="The Thief and the Dogs")
        
        author1.books.extend([book1, book2])
        author2 = Author(name="Ahmed Khaled Towfiq")
        
        # add_all(): Synchronous state operation. Does not hit the database yet.
        session.add_all([author1, author2])

        # flush(): Awaitable. Sends SQL to the database to assign IDs without committing.
        await session.flush() 
        
        # commit(): Awaitable. Finalizes the transaction safely.
        await session.commit()

        # Async Querying: select() wrapped in session.execute()
        stmt = select(Author).where(Author.name == "Nagib Mahfouz")
        result = await session.execute(stmt)
        target_author = result.scalar_one_or_none()
        
        if target_author:
            target_author.name = "Ali"
            await session.commit()
            
            # refresh(): Awaitable. Reloads state from the database.
            await session.refresh(target_author)

        # delete(): Synchronous state marking. The actual execution happens on commit.
        await session.delete(author2)
        await session.commit()

        # expunge(): Synchronous cache eviction.
        session.expunge(author1)

    except Exception as e:
        # rollback(): Awaitable. Reverts pending I/O operations and unlocks rows.
        await session.rollback()
        print(f"Transaction failed: {e}")
        sys.exit(1)
    finally:
        # close(): Awaitable. Returns the underlying connection to the async pool.
        await session.close()

    # dispose(): Awaitable. Closes all background pool connections properly.
    await engine.dispose()

if __name__ == "__main__":
    # asyncio.run() manages the event loop for the execution of the main coroutine.
    asyncio.run(main())


"""
# ---------------------------------------------------------
# Relationship Mapping Examples (Declarative 2.0 - AsyncIO)
# Note: Always include lazy="selectin" to avoid I/O blocking errors.
# ---------------------------------------------------------

# 1. One-to-One (1:1)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    profile: Mapped[Optional["Profile"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    user: Mapped["User"] = relationship(back_populates="profile", lazy="selectin")


# 2. One-to-Many (1:N)
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    employees: Mapped[List["Employee"]] = relationship(
        back_populates="department", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship(back_populates="employees", lazy="selectin")


# 3. Many-to-Many (M:N)
student_course_table = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True)
)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    courses: Mapped[List["Course"]] = relationship(
        secondary=student_course_table, 
        back_populates="students",
        lazy="selectin"
    )

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    students: Mapped[List["Student"]] = relationship(
        secondary=student_course_table, 
        back_populates="courses",
        lazy="selectin"
    )
"""
