from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.database.sqlalchemy_models.base import Base


class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True
    )  # if nullable Mapped[str|None]
    version_id: Mapped[int]

    # رسل أوامر مباشرة لمحرك SQLAlchemy
    #  الداخلي الذي يدير دورة حياة الكائن وسلوك الاستعلامات.

    __mapper_args__ = {
        "version_id_col": version_id,  # it's add AND version_id = {number} to Where automiticlly
        "version_id_generator": False,  # do not increases =+1 in the update automiticlly
    }
