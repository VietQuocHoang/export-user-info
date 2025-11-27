from typing import List

from sqlalchemy import JSON, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    org_config: Mapped[dict] = mapped_column(JSON, nullable=True)
    users: Mapped[List["User"]] = relationship(back_populates="organization")
