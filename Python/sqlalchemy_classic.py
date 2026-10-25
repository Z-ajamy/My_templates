#1. classical SqlAlchemy
from sys import argv

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import registry, relationship, sessionmaker

metadata = MetaData()
authors_table = Table("authors", metadata, Column('id', Integer, primary_key=True), Column("name", String(100), nullable=False))

books_table = Table("books", metadata, Column("id", Integer, primary_key=True), Column("title", String(150), nullable=False), Column("author_id", Integer, ForeignKey("authors.id"), nullable=False))


class Author:
    def __init__(self, name):
        self.name = name

class Book:
    def __init__(self, title):
        self.title = title

reg = registry()

reg.map_imperatively(Author, authors_table, properties={
    "books": relationship(
        Book,
        back_populates="author",
        cascade="all, delete-orphan"
    )
})

reg.map_imperatively(Book, books_table, properties={
    "author": relationship(
        Author,
        back_populates="books",
    )
})

if __name__ == "__main__":
    link = argv[1]
    engin = create_engine(link)
    metadata.create_all(engin)

    Sess = sessionmaker(bind=engin)
    s = Sess()

    author1 = Author("Nagib Mahfouz")

    book1 = Book("b1")
    book2 = Book("b2")

    author1.books.append(book1)
    author1.books.append(book2)

    s.add(author1)

    s.commit()

    all_authors = s.query(Author).all()
    all_authors[0].name = "Ali"

    s.commit()
    s.close()
    engin.expose()

