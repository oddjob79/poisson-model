from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import (
    ForeignKey, 
    String, 
    SmallInteger,
    DateTime,
    Identity,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.team import Team


class Fixture(Base):
    __tablename__ = "fixtures"
    id: Mapped[int] = mapped_column(
        Identity(start=1, always=True), primary_key=True
    )

    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"))
    competition: Mapped["Competition"] = relationship(
        back_populates="fixtures", foreign_keys=[competition_id]
    )

    timestamp_utc: Mapped[datetime] = mapped_column(DateTime)

    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    home_team: Mapped["Team"] = relationship(
        back_populates="home_fixtures", foreign_keys=[home_team_id]
    )

    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    away_team: Mapped["Team"] = relationship(
        back_populates="away_fixtures", foreign_keys=[away_team_id]
    )

    ht_home: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    ht_away: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    ft_home: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    ft_away: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    result: Mapped[str] = mapped_column(String(1), nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "competition_id", 
            "home_team_id", 
            'away_team_id', 
            name="uq_fixture_competition_home_team_away_team"),
    )    

    def __repr__(self) -> str:
        return (
            f"Fixture(id={self.id!r}, {self.timestamp_utc}: "
            f"{self.home_team.name!r} - {self.away_team.name!r})"
        )