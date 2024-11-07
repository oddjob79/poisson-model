from typing import List
from sqlalchemy import (
    UniqueConstraint, 
    Identity, 
    String, 
    SmallInteger,
    Table,
    Column,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
import models


team_competition = Table(
    "team_competition",
    models.Base.metadata,
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
    Column("competition_id", ForeignKey("competitions.id"), primary_key=True),
)


class Competition(models.Base):
    __tablename__ = "competitions"
    id: Mapped[int] = mapped_column(
        Identity(start=1, always=True), primary_key=True
    )

    name: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(SmallInteger)
    short_name: Mapped[str] = mapped_column(String(8))
    country: Mapped[str] = mapped_column(String(20))
    alt_id: Mapped[int] = mapped_column(SmallInteger)

    teams: Mapped[List["models.Team"]] = relationship(
        secondary=team_competition, back_populates="competitions"
    )

    fixtures: Mapped[List["models.Fixture"]] = relationship(
        back_populates="competition", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("name", "year", name="uq_competition_name_year"),
    )

    def __repr__(self) -> str:
        return (
            f"Competition(id={self.id!r}, name={self.name!r}, "
            f"year={self.year!r})"
        )
