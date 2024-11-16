import json
import sys
from typing import List
from requests import request
from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as upsert

from app.conn import Session
from app.config import Config
from app.models.competition import Competition, team_competition
from app.models.team import Team
from app.models.fixture import Fixture


league_url="https://v3.football.api-sports.io/leagues?country=England&type=league"
team_url = ""
fixture_url = ""


map__lg_name__short_name = {
    "Premier League": "EPL",
    "Championship": "CHP",
    "League One": "L1",
    "League Two": "L2",
    "National League": "NTL",
}


def json_to_dictlist(filename: str) -> List[dict]:
    with open(filename) as f_in:
        return json.load(f_in)["response"]


def parse_fixtures(
    fixtures: List[dict],
    competition_id: int,
    teams: List[Team],
) -> List[dict]:
    def determine_result(
        fulltime_home: int | None, 
        fulltime_away: int | None
    ) -> str:
        if fulltime_home is None:
            return None
        if fulltime_home > fulltime_away:
            return "H"
        if fulltime_home < fulltime_away:
            return "A"
        if fulltime_home == 0 and fulltime_away == 0:
            return "D"
        if fulltime_home > 0 and fulltime_away > 0:
            return "X"

    def get_team_id(team_id: int) -> int:
        return [t.id for t in teams if t.alt_id == team_id][0]

    fixture_list = list()
    for f in fixtures:
        result = determine_result(
            fulltime_home=f["score"]["fulltime"]["home"],
            fulltime_away=f["score"]["fulltime"]["away"],
        )

        fixture_list.append(
            {
                "timestamp_utc": f["fixture"]["date"],
                "competition_id": competition_id,
                "home_team_id": get_team_id(f["teams"]["home"]["id"]),
                "away_team_id": get_team_id(f["teams"]["away"]["id"]),
                "ht_home": f["score"]["halftime"]["home"],
                "ht_away": f["score"]["halftime"]["away"],
                "ft_home": f["score"]["fulltime"]["home"],
                "ft_away": f["score"]["fulltime"]["away"],
                "result": result,
            }
        )

    return fixture_list


def parse_leagues(leagues: List[dict]) -> List[dict]:
    leagues = [
        {
            "name": league["league"]["name"],
            "year": season["year"],
            "short_name": map__lg_name__short_name[league["league"]["name"]],
            "country": league["country"]["name"],
            "alt_id": league["league"]["id"],
        }
        for league in leagues for season in league["seasons"]
        if league["league"]["id"] in [39, 40, 41, 42, 43]
        and season["year"] in [2023, 2024]
    ]
    return leagues


def parse_teams(teams: List[dict]) -> List[dict]:
    teams = [
        {
            "name": team["team"]["name"],
            "short_name": team["team"]["code"],
            "country": team["team"]["country"],
            "alt_id": team["team"]["id"],
        }
        for team in teams
    ]

    return teams


# def lookup_competition(league: int, season: int) -> int:



# def parse_competition_teams(
#     teams: List[dict], 
#     league: int, 
#     season: int
# ) -> List[dict]:
    


table_map = {
    "leagues": {
        "parser": parse_leagues, 
        "url": league_url, 
        "model": Competition,
    },
    "teams": {
        "parser": parse_teams, 
        "url": team_url,
        "model": Team,
    },
    "fixtures": {
        "parser": parse_fixtures, 
        "url": fixture_url,
        "model": Fixture
    }
}


def get_from_api(url: str) -> dict:
    headers = {"x-apisports-key": Config.API_KEY}

    response = request("GET", url, headers=headers)
    res = json.loads(response.text)

    return res.get("response")


def teams_handler():
    session = Session()
    competitions = session.scalars(select(Competition)).all()
    for c in competitions:
        # print(f"{c.name}, {c.year}")
        # print(c.alt_id, c.year)
        # print(f"https://v3.football.api-sports.io/teams?league={c.alt_id}&season={c.year}")
        url = f"https://v3.football.api-sports.io/teams?league={c.alt_id}&season={c.year}"

        api_teams = get_from_api(url=url)
        teams = parse_teams(api_teams)

        try:
            insert_stmt = upsert(Team).values(teams)
            stmt = insert_stmt.on_conflict_do_update(
                constraint="uq_team_name_country", 
                set_=dict(short_name=insert_stmt.excluded.short_name)
            )
            insert_teams = session.scalars(stmt.returning(Team))
            # inst_teams = session.scalars(insert(Team).returning(Team), teams)
            for t in insert_teams.all():
                session.execute(
                    team_competition.insert().values(
                        team_id=t.id, competition_id=c.id
                    )
                )
                # c.teams.append(t)
        except Exception as e:
            print(f'Insert / update team fail. {e}')
            session.rollback()
        else:
            print('Insert team data successful.')
            session.commit()


def fixture_handler():
    session = Session()
    teams = session.scalars(select(Team)).all()    
    competitions = session.scalars(select(Competition)).all()
    for c in competitions:
        # print(f"https://v3.football.api-sports.io/fixtures?league={c.alt_id}&season={c.year}")
        url = f"https://v3.football.api-sports.io/fixtures?league={c.alt_id}&season={c.year}"

        api_fixtures = get_from_api(url=url)
        fixture_data = parse_fixtures(
            fixtures=api_fixtures, 
            competition_id=c.id,
            teams=[t for t in teams if c in t.competitions],
        )

        try:
            insert_stmt = upsert(Fixture).values(fixture_data)
            stmt = insert_stmt.on_conflict_do_update(
                constraint="uq_fixture_competition_home_team_away_team", 
                set_=dict(
                    timestamp_utc=insert_stmt.excluded.timestamp_utc,
                    ht_home=insert_stmt.excluded.ht_home,
                    ht_away=insert_stmt.excluded.ht_away,
                    ft_home=insert_stmt.excluded.ft_home,
                    ft_away=insert_stmt.excluded.ft_away,
                    result=insert_stmt.excluded.result,
                )
            )
            session.execute(stmt)
        except Exception as e:
            print(f'Insert fixtures fail. {e}')
            session.rollback()
        else:
            print('Insert fixtures data successful.')
            session.commit()    


def handler(table: str):
    # eng_leagues = json_to_dictlist(filename="./app/data/leagues_new.json")
    # season_fixtures = parse_fixtures(fixtures=fixtures)

    if table not in ["leagues", "teams", "fixtures"]:
        raise ValueError("Unavailable table load. Exiting")

    # try:
    #     model = table_map[table]["model"]
    #     data = table_map[table]["parser"](
    #         get_from_api(url=table_map[table]["url"])
    #     )
    # except Exception as e:
    #     print(f"Error retrieving and/or parsing data. {e}")


    if table == "leagues":
        model = Competition
        try:
            data = parse_leagues(leagues=get_from_api(url=league_url))
        except Exception as e:
            print(f"Error retrieving and/or parsing data. {e}")
    
    elif table == "teams":
        teams_handler()
        return
        # model = Team
        # try:
        #     session = Session()
        #     competitions = session.scalars(
        #         select(Competition)
        #     ).all()
        #     for c in competitions:
        #         # print(f"{c.name}, {c.year}")
        #         # print(c.alt_id, c.year)
        #         print(f"https://v3.football.api-sports.io/teams?league={c.alt_id}&season={c.year}")
            
        #     # data = parse_teams(teams=get_from_api(url=team_url))
        # except Exception as e:
        #     print(f"Error retrieving and/or parsing data. {e}")

    elif table == "fixtures":
        try:
            fixture_handler()
            return
        except Exception as e:
            print(f"Error handling fixtures. {e}")


    # try:
    #     print("Data retrieved")
    #     session = Session()
    #     session.execute(insert(model), data)
    # except Exception as e:
    #     print(f"Error in league load. {e}")
    #     session.rollback()
    # else:
    #     session.commit()
    #     print("Data committed. End.")


if __name__ == "__main__":
    table = sys.argv[1] if sys.argv[1] else None
    print(f"Script loaded with arg {table}")
    handler(table=table)
