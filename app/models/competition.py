from typing import List, TYPE_CHECKING
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
from app.models.base import Base
if TYPE_CHECKING:
    from app.models.fixture import Fixture
    from app.models.team import Team

from functools import reduce

team_competition = Table(
    "team_competition",
    Base.metadata,
    Column("team_id", ForeignKey("teams.id"), primary_key=True),
    Column("competition_id", ForeignKey("competitions.id"), primary_key=True),
)


class Competition(Base):
    __tablename__ = "competitions"
    id: Mapped[int] = mapped_column(
        Identity(start=1, always=True), primary_key=True
    )

    name: Mapped[str] = mapped_column(String(50))
    year: Mapped[int] = mapped_column(SmallInteger)
    short_name: Mapped[str] = mapped_column(String(8))
    country: Mapped[str] = mapped_column(String(20))
    alt_id: Mapped[int] = mapped_column(SmallInteger)

    teams: Mapped[List["Team"]] = relationship(
        secondary=team_competition, back_populates="competitions"
    )

    fixtures: Mapped[List["Fixture"]] = relationship(
        back_populates="competition", cascade="all, delete-orphan"
    )

    # calculated fields
    total_home_goals: Mapped[int] = sum([f.ft_home for f in fixtures])
    # total_away_goals: Mapped[int] = sum([f.ft_away for f in fixtures])
    # total_goals: Mapped[int] = total_home_goals + total_away_goals
    # avg_goals_per_game: Mapped[int]
    # avg_home_goals_per_game: Mapped[int]
    # avg_away_goals_per_game: Mapped[int]


    __table_args__ = (
        UniqueConstraint("name", "year", name="uq_competition_name_year"),
    )

    def __repr__(self) -> str:
        return (
            f"Competition(id={self.id!r}, name={self.name!r}, "
            f"year={self.year!r})"
        )
