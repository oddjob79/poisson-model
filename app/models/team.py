from typing import List, TYPE_CHECKING
from sqlalchemy import String, Identity, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.competition import team_competition
if TYPE_CHECKING:
    from app.models.competition import Competition
    from app.models.fixture import Fixture


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(
        Identity(start=1, always=True), primary_key=True
    )

    name: Mapped[str] = mapped_column(String(50))
    short_name: Mapped[str] = mapped_column(String(8), nullable=True)
    country: Mapped[str] = mapped_column(String(20))
    alt_id: Mapped[int] = mapped_column(SmallInteger)

    competitions: Mapped[List["Competition"]] = relationship(
        secondary=team_competition, back_populates="teams"
    )

    home_fixtures: Mapped[List["Fixture"]] = relationship(
        back_populates="home_team", foreign_keys="Fixture.home_team_id"
    )

    away_fixtures: Mapped[List["Fixture"]] = relationship(
        back_populates="away_team", foreign_keys="Fixture.away_team_id"
    )

    __table_args__ = (
        UniqueConstraint("name", "country", name="uq_team_name_country"),
    )    

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, name={self.name!r})"
