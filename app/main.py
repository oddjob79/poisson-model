from sqlalchemy import select

from typing import List
from app.conn import Session
from app.models.fixture import Fixture
from app.models.competition import Competition
from app.models.team import Team


session = Session()


def calc_competition_stats() -> List[dict]:
    comps = session.scalars(select(Competition)).all()

    comp_stats = list()
    for c in comps:
        home_goals = [f.ft_home for f in c.fixtures if f.ft_home is not None]
        away_goals = [f.ft_away for f in c.fixtures if f.ft_away is not None]

        total_home_goals = sum(home_goals)
        total_away_goals = sum(away_goals)

        avg_home_goals = total_home_goals / len(home_goals)
        avg_away_goals = total_away_goals / len(away_goals)

        comp_stats.append(
            {
                "competition_id": c.id,
                "name": c.name,
                "year": c.year,
                "total_home_goals": total_home_goals,
                "total_away_goals": total_away_goals,
                "avg_home_goals": avg_home_goals,
                "avg_away_goals": avg_away_goals,
            }
        )

    print(comp_stats)
    return comp_stats


def calc_current_team_stats(comp_stats):
    teams = session.scalars(select(Team)).all()
    team_list = list()

    for t in teams:
        total_home_goals = tuple(
            (f.ft_home, f.ft_away, f.competition_id)
            for f in t.home_fixtures
            if f.ft_home is not None and f.competition.year == 2024
        )

        total_away_goals = tuple(
            (f.ft_home, f.ft_away)
            for f in t.away_fixtures
            if f.ft_home is not None and f.competition.year == 2024
        )

        competition_id = max(hg[2] for hg in total_home_goals)
        total_hg_scored = sum([hg[0] for hg in total_home_goals])
        total_hg_conceded = sum([hg[1] for hg in total_home_goals])
        total_ag_scored = sum([ag[1] for ag in total_away_goals])
        total_ag_conceded = sum([ag[0] for ag in total_away_goals])

        team_list.append(
            {
                "team_id": t.id,
                "name": t.name,
                "competition_id": competition_id,
                "total_home_goals_scored": total_hg_scored,
                "total_home_goals_conceded": total_hg_conceded,
                "total_home_games_played": len(total_home_goals),
                "avg_hg_scored": total_hg_scored / len(total_home_goals),
                "avg_hg_conceded": total_hg_conceded / len(total_home_goals),
                "total_away_goals_scored": total_ag_scored,
                "total_away_goals_conceded": total_ag_conceded,
                "total_away_games_played": len(total_away_goals),
                "avg_ag_scored": total_ag_scored / len(total_away_goals),
                "avg_ag_conceded": total_ag_conceded / len(total_away_goals),
            }
        )

    return team_list


def handler():
    # res = session.scalars(
    #     select(Fixture).where(Fixture.competition_id==1)
    # ).all()

    # home_goals = [r.ft_home for r in res]
    # away_goals = [r.ft_away for r in res]

    comp_stats = calc_competition_stats()


if __name__ == "__main__":
    handler()
