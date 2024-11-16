import json
from typing import List
from sqlalchemy import insert
from app.conn import Session
from app.models.competition import Competition


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


def parse_fixtures(fixtures: List[dict]) -> List[dict]:
    return [
        {
            "id": f["fixture"]["id"],
            "date": f["fixture"]["date"],
            "status": f["fixture"]["status"]["short"],
            "league_id": f["league"]["id"],
            "league_name": f["league"]["name"],
            "season": f["league"]["season"],
            "round": f["league"]["round"],
            "home_id": f["teams"]["home"]["id"],
            "home_name": f["teams"]["home"]["name"],
            "home_ht_goals": f["score"]["halftime"]["home"],
            "home_ft_goals": f["goals"]["home"],
            "away_id": f["teams"]["away"]["id"],
            "away_name": f["teams"]["away"]["name"],
            "away_ht_goals": f["score"]["halftime"]["away"],
            "away_ft_goals": f["goals"]["away"],
        }
        for f in fixtures
    ]


def parse_leagues(leagues: str) -> List[dict]:
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


def handler():
    eng_leagues = json_to_dictlist(filename="./app/data/leagues_new.json")
    # season_fixtures = parse_fixtures(fixtures=fixtures)
    league_data = parse_leagues(leagues=eng_leagues)

    print(league_data)

    # session = Session()
    # session.execute(insert(Competition), league_data)




if __name__ == "__main__":
    # print('hello')
    handler()
