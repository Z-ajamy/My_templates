import sys
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Base class for declarative class definitions
Base = declarative_base()

class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    
    # cascade="all, delete-orphan": Instructs SQLAlchemy to propagate deletion. 
    # If an Author is deleted, all their associated Books are automatically deleted.
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    
    author = relationship("Author", back_populates="books")


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <database_url>")
        sys.exit(1)
        
    db_url = sys.argv[1]

    # Engine Configuration Hints:
    # pool_pre_ping=True: Tests the connection for liveness upon each checkout. Crucial for production.
    # pool_size: The number of connections to keep open. Formula hint: (CPU Cores * 2) + Spindles.
    # max_overflow: How many connections to allow beyond pool_size when under load before blocking.
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,       
        max_overflow=20     
    )
    
    # Create all tables bounded to the Base metadata
    Base.metadata.create_all(engine)

    # Session Configuration Hints:
    # expire_on_commit=False: Prevents SQLAlchemy from expiring object attributes after commit(). 
    #                         Reduces lazy loading overhead if you need the data post-commit.
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    
    session = SessionLocal()

    try:
        # Instantiation
        author1 = Author(name="Nagib Mahfouz")
        book1 = Book(title="Children of the Alley")
        book2 = Book(title="The Thief and the Dogs")
        
        # Append to relationship collection
        author1.books.extend([book1, book2])
        
        author2 = Author(name="Ahmed Khaled Towfiq")
        
        # session.add_all(): Bulk inserts objects into the session's pending state.
        session.add_all([author1, author2])

        # flush(): Sends SQL commands to DB and retrieves generated PKs, but DOES NOT commit.
        session.flush() 
        
        # commit(): Finalizes the transaction.
        session.commit()

        # Update operation
        # Using the classic query style as requested
        target_author = session.query(Author).filter_by(name="Nagib Mahfouz").first()
        if target_author:
            target_author.name = "Ali"
            session.commit()
            
            # refresh(): Reloads the object's state from the database.
            session.refresh(target_author)

        # Deletion
        # delete(): Marks the object for deletion. Cascades will trigger based on relationship config.
        session.delete(author2)
        session.commit()

        # Expunge (Eviction)
        # expunge(): Removes a specific object from the session tracking.
        session.expunge(author1)
        
        # expunge_all(): Clears all objects from the session.
        # session.expunge_all()

    except Exception as e:
        # rollback(): Reverts all pending changes in the current transaction.
        session.rollback()
        print(f"Transaction failed: {e}")
        sys.exit(1)
    finally:
        # close(): Returns the connection back to the connection pool. MUST be executed.
        session.close()

    # dispose(): Closes all connections in the connection pool completely.
    engine.dispose()

if __name__ == "__main__":
    main()


"""
# ---------------------------------------------------------
# Relationship Mapping Examples (Declarative)
# ---------------------------------------------------------

# 1. One-to-One (1:1)
# Use `uselist=False` on the parent relationship to enforce a scalar (single object).
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True) # unique=True enforces 1:1 at DB level
    
    user = relationship("User", back_populates="profile")


# 2. One-to-Many (1:N)
# Identical to the Author/Book relationship above. Parent holds a collection.
class Department(Base):
    __tablename__ = "departments"
    id = Column(Integer, primary_key=True)
    
    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("departments.id"))
    
    department = relationship("Department", back_populates="employees")


# 3. Many-to-Many (M:N)
# Requires an Association Table defined as a classic `Table` object, NOT a declarative class.
student_course_table = Table(
    "student_course", 
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    
    # secondary parameter points to the association table
    courses = relationship("Course", secondary=student_course_table, back_populates="students")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    
    students = relationship("Student", secondary=student_course_table, back_populates="courses")
"""
