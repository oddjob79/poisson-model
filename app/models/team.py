from typing import List
from sqlalchemy import String, Identity, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

import models
from models.competition import team_competition


class Team(models.Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(
        Identity(start=1, always=True), primary_key=True
    )

    name: Mapped[str] = mapped_column(String(50))
    short_name: Mapped[str] = mapped_column(String(8))
    country: Mapped[str] = mapped_column(String(20))
    alt_id: Mapped[int] = mapped_column(SmallInteger)

    competitions: Mapped[List["models.Competition"]] = relationship(
        secondary=team_competition, back_populates="teams"
    )

    home_fixtures: Mapped[List["models.Fixture"]] = relationship(
        back_populates="home_team"
    )

    away_fixtures: Mapped[List["models.Fixture"]] = relationship(
        back_populates="away_team"
    )

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, name={self.name!r})"
