import sys
import json
from typing import List


def json_to_dictlist(filename: str) -> List[dict]:
    with open(filename) as f_in:
        return json.load(f_in)['response']


def parse_fixtures(fixtures: List[dict]) -> List[dict]:
    return [
        {
            "id": f['fixture']['id'],
            "date": f['fixture']['date'],
            "status": f['fixture']['status']['short'],
            "league_id": f['league']['id'],
            "league_name": f['league']['name'],
            "season": f['league']['season'],
            "round": f['league']['round'],
            "home_id": f['teams']['home']['id'],
            "home_name": f['teams']['home']['name'],
            "home_ht_goals": f['score']['halftime']['home'],
            "home_ft_goals": f['goals']['home'],
            "away_id": f['teams']['away']['id'],
            "away_name": f['teams']['away']['name'],
            "away_ht_goals": f['score']['halftime']['away'],
            "away_ft_goals": f['goals']['away']
        } for f in fixtures
    ]
    

def handler(week=None):
    print(week)

    fixtures = json_to_dictlist(filename='./data/fixtures.json')
    season_fixtures = parse_fixtures(fixtures=fixtures)


if __name__ == "__main__":
    # print('hello')
    week = sys.argv[1] if sys.argv[1] else None
    handler(week=week)
