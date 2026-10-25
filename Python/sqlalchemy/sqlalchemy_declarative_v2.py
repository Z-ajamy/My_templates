import sys
from typing import List, Optional
from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# 1. Base Class for Declarative 2.0
class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    
    # mapped_column() replaces Column() in 2.0. Mapped[type] is required for static typing.
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    
    # cascade="all, delete-orphan": Deletes orphan books when removed from author.books or when author is deleted.
    books: Mapped[List["Book"]] = relationship(back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))
    
    author: Mapped["Author"] = relationship(back_populates="books")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <database_url>")
        sys.exit(1)
        
    db_url = sys.argv[1]

    # pool_pre_ping=True: Validates connection health before checkout to avoid "server has gone away" errors.
    # pool_size=10, max_overflow=20: Tunes connection pool capacity based on hardware threads and DB limits.
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,       
        max_overflow=20     
    )
    
    Base.metadata.create_all(engine)

    # expire_on_commit=False: Keeps instances fully loaded in memory after commit, avoiding DetachedInstanceError.
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    try:
        # Instantiation
        author1 = Author(name="Nagib Mahfouz")
        book1 = Book(title="Children of the Alley")
        book2 = Book(title="The Thief and the Dogs")
        
        author1.books.extend([book1, book2])
        author2 = Author(name="Ahmed Khaled Towfiq")
        
        # add_all(): Stages multiple instances to the session.
        session.add_all([author1, author2])

        # flush(): Emits SQL to the database to get auto-generated IDs without committing the transaction.
        session.flush() 
        session.commit()

        # SQLAlchemy 2.0 Query Style (select + execute)
        # scalar_one_or_none(): Returns exactly one result or None. Raises error if multiple exist.
        stmt = select(Author).where(Author.name == "Nagib Mahfouz")
        target_author = session.execute(stmt).scalar_one_or_none()
        
        if target_author:
            target_author.name = "Ali"
            session.commit()
            
            # refresh(): Updates the instance state directly from the database.
            session.refresh(target_author)

        # delete(): Marks the instance for deletion. Cascades execute upon commit.
        session.delete(author2)
        session.commit()

        # expunge(): Detaches a specific instance from the session.
        session.expunge(author1)

    except Exception as e:
        # rollback(): Critical to clear pending changes and release locks on error.
        session.rollback()
        print(f"Transaction failed: {e}")
        sys.exit(1)
    finally:
        # close(): Releases the connection back to the pool. Mandatory to prevent connection exhaustion.
        session.close()

    # dispose(): Shuts down the engine and terminates all physical connections.
    engine.dispose()

if __name__ == "__main__":
    main()


"""
# ---------------------------------------------------------
# Relationship Mapping Examples (Declarative 2.0)
# ---------------------------------------------------------

# 1. One-to-One (1:1)
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Optional["Profile"] and uselist=False enforce single object instead of a list.
    profile: Mapped[Optional["Profile"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True) # unique=True at DB level
    
    user: Mapped["User"] = relationship(back_populates="profile")


# 2. One-to-Many (1:N)
# Same concept as Author/Book above.
class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(primary_key=True)
    employees: Mapped[List["Employee"]] = relationship(back_populates="department", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    department: Mapped["Department"] = relationship(back_populates="employees")


# 3. Many-to-Many (M:N)
# The association table remains a classic Table object, wrapped in Base.metadata.
student_course_table = Table(
    "student_course",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("course_id", ForeignKey("courses.id"), primary_key=True)
)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(primary_key=True)
    courses: Mapped[List["Course"]] = relationship(secondary=student_course_table, back_populates="students")

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(primary_key=True)
    students: Mapped[List["Student"]] = relationship(secondary=student_course_table, back_populates="courses")
"""
