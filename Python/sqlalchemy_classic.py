import sys
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship, sessionmaker

metadata = MetaData()

authors_table = Table(
    "authors", 
    metadata, 
    Column('id', Integer, primary_key=True), 
    Column("name", String(100), nullable=False)
)

books_table = Table(
    "books", 
    metadata, 
    Column("id", Integer, primary_key=True), 
    Column("title", String(150), nullable=False), 
    Column("author_id", Integer, ForeignKey("authors.id"), nullable=False)
)

class Author:
    def __init__(self, name):
        self.name = name
        self.books = [] # Initialization for the relationship

class Book:
    def __init__(self, title):
        self.title = title

reg = registry()

# cascade="all, delete-orphan": Instructs SQLAlchemy to propagate deletion. 
# If an Author is deleted, all their associated Books are automatically deleted.
# If a Book is removed from author.books, it gets deleted from the database.
reg.map_imperatively(Author, authors_table, properties={
    "books": relationship(Book, back_populates="author", cascade="all, delete-orphan")
})

reg.map_imperatively(Book, books_table, properties={
    "author": relationship(Author, back_populates="books")
})

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <database_url>")
        sys.exit(1)
        
    db_url = sys.argv[1]

    # Engine Configuration Hints:
    # pool_pre_ping=True: Tests the connection for liveness upon each checkout. Crucial for preventing "MySQL server has gone away" or broken pipe errors in production.
    # pool_size: The number of connections to keep open. Formula hint: (CPU Cores * 2) + Spindles. For an architecture like AMD Ryzen 3 (4 Cores), pool_size=10 to 15 is optimal for I/O bound tasks.
    # max_overflow: How many connections to allow beyond pool_size when under load before blocking.
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=10,       
        max_overflow=20     
    )
    
    metadata.create_all(engine)

    # Session Configuration Hints:
    # expire_on_commit=False: Prevents SQLAlchemy from expiring object attributes after commit(). 
    #                         Useful if you need to access object data after the transaction ends without triggering another database query (reduces lazy loading overhead).
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    
    session = SessionLocal()

    try:
        author1 = Author("Nagib Mahfouz")
        book1 = Book("Children of the Alley")
        book2 = Book("The Thief and the Dogs")
        author1.books.extend([book1, book2])
        
        author2 = Author("Ahmed Khaled Towfiq")
        
        # session.add_all(): Bulk inserts objects into the session's pending state.
        session.add_all([author1, author2])

        # flush(): Communicates with the database, sending the SQL commands (INSERT/UPDATE/DELETE) and retrieving generated primary keys, but DOES NOT commit the transaction. Changes can still be rolled back.
        session.flush() 
        
        # commit(): Finalizes the transaction, making the changes permanently visible to other database connections.
        session.commit()

        # Update operation
        author1.name = "Ali"
        session.commit()
        
        # refresh(): Reloads the object's state from the database, overwriting any unsaved in-memory changes.
        session.refresh(author1)

        # Deletion
        # delete(): Marks the object for deletion. Due to cascade="all, delete-orphan", related books will also be deleted upon commit.
        session.delete(author2)
        session.commit()

        # Expunge (Eviction)
        # expunge(): Removes a specific object from the session. It becomes "detached" and changes to it will no longer be tracked.
        session.expunge(author1)
        
        # expunge_all(): Clears all objects from the session entirely.
        # session.expunge_all()

    except Exception as e:
        # rollback(): Reverts all pending changes in the current transaction if an error occurs, keeping the database in a consistent state.
        session.rollback()
        print(f"Transaction failed: {e}")
        sys.exit(1)
    finally:
        # close(): Returns the connection back to the connection pool. MUST be executed to prevent connection leaks.
        session.close()

    # dispose(): Closes all connections in the connection pool completely. Essential during application shutdown or process forking.
    engine.dispose()

if __name__ == "__main__":
    main()

"""
# ---------------------------------------------------------
# Relationship Mapping Examples (Imperative)
# ---------------------------------------------------------

# 1. One-to-One (1:1)
# Use `uselist=False` on the parent relationship to enforce a scalar (single object) rather than a collection.
reg.map_imperatively(User, users_table, properties={
    "profile": relationship(Profile, back_populates="user", uselist=False, cascade="all, delete-orphan")
})
reg.map_imperatively(Profile, profiles_table, properties={
    "user": relationship(User, back_populates="profile")
})


# 2. One-to-Many (1:N)
# Identical to the Author/Book relationship implemented in the code above. The parent holds a list/collection of children.
reg.map_imperatively(Department, departments_table, properties={
    "employees": relationship(Employee, back_populates="department", cascade="all, delete-orphan")
})
reg.map_imperatively(Employee, employees_table, properties={
    "department": relationship(Department, back_populates="employees")
})


# 3. Many-to-Many (M:N)
# Requires an Association Table (a Table object without a mapped Python class) referencing both parent tables via ForeignKeys.
student_course_table = Table("student_course", metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True)
)

reg.map_imperatively(Student, students_table, properties={
    "courses": relationship(Course, secondary=student_course_table, back_populates="students")
})
reg.map_imperatively(Course, courses_table, properties={
    "students": relationship(Student, secondary=student_course_table, back_populates="courses")
})
"""
