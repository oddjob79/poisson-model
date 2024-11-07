from datetime import datetime
from sqlalchemy import (
    ForeignKey, 
    String, 
    SmallInteger,
    DateTime,
    Identity,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
# from models import Base, Team, Competition
# from models.base import Base
# from models.competition import Competition
# from models.team import Team
import models


class Fixture(models.Base):
    __tablename__ = "fixtures"
    id: Mapped[int] = mapped_column(
        Identity(start=1, always=True), primary_key=True
    )

    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"))
    competition: Mapped["models.Competition"] = relationship(
        back_populates="fixtures"
    )

    timestamp_utc: Mapped[datetime] = mapped_column(DateTime)

    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    home_team: Mapped["models.Team"] = relationship(
        back_populates="home_fixtures", foreign_keys=[home_team_id]
    )

    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team: Mapped["models.Team"] = relationship(
        back_populates="away_fixtures", foreign_keys=[away_team_id]
    )

    ht_home: Mapped[int] = mapped_column(SmallInteger)
    ht_away: Mapped[int] = mapped_column(SmallInteger)
    ft_home: Mapped[int] = mapped_column(SmallInteger)
    ft_away: Mapped[int] = mapped_column(SmallInteger)
    result: Mapped[str] = mapped_column(String(1))

    def __repr__(self) -> str:
        return (
            f"Team(id={self.id!r}, {self.home_team.short_name!r} "
            f"{self.ft_home!r}-{self.ft_away!r} {self.away_team.short_name!r})"
        )