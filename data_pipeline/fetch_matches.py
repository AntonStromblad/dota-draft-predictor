import cloudscraper
import json
import time
import os
import requests

STRATZ_TOKEN = "KEY"

def fetch_hero_picks(total_leagues_to_check=10, matches_per_league=50):
    all_matches = []
    
    headers = {
        "Authorization": f"Bearer {STRATZ_TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }


    scraper = cloudscraper.create_scraper()
    for skip_league in range(0, total_leagues_to_check):
        query = """
        query GetProPicks($skipLeague: Int!, $matchesPerLeague: Int!) {
          leagues(request: { take: 1, skip: $skipLeague, tiers: [PROFESSIONAL], orderBy: LAST_MATCH_TIME_THEN_TIER }) {
            displayName
            matches(request: { take: $matchesPerLeague, skip: 0, isParsed: true }) {
              id
              didRadiantWin
              rank
              players {
                isRadiant
                heroId
                hero {
                  displayName
                }
              }
            }
          }
        }
        """
        
        variables = {
            "skipLeague": skip_league,
            "matchesPerLeague": matches_per_league
        }
        API_URL = ""
        response = scraper.post(
            API_URL, 
            json={"query": query, "variables": variables}, 
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            leagues = data.get('data', {}).get('leagues', [])
            
            if not leagues:
                print("Hittade inga fler ligor.")
                break
                
            for league in leagues:
                matches = league.get('matches', [])
                valid_matches = []
                if not matches:
                    continue
                for match in matches:
                    rank = match.get('rank', [])

                    if rank >= 80:
                        #Ska vara högre än immoral
                        valid_matches.append(match)
                
                if valid_matches:
                    all_matches.extend(valid_matches)                    
        else:
            break
            
        time.sleep(1)

    file_path = "raw_data/pro_picks.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_matches, f, indent=2, ensure_ascii=False)


def fetch_heroId_to_name():
    response = requests.get("https://api.opendota.com/api/heroes",[])
    heroes_data = response.json()


    hero_dict = {hero["id"] : hero["localized_name"] for chunk in heroes_data for hero in chunk}
    print(hero_dict)


def fetch_hero_picks_normal_matches():
    all_matches = []
    responses = requests.get("https://api.opendota.com/api/publicMatches", params={"min_rank" : 80}).json()
    for response in responses:
        match = {}
        match_id = response.get("match_id",0)
        radiant_win = response.get("radiant_win", True)
        rank = response.get("avg_rank_tier", 75)
        radiant_team : dict= response.get("radiant_team", [])
        dire_team = response.get("dire_team", [])
        players = []
        for player,hero_id in radiant_team:
            {"isRadiant": True, "heroId":hero_id, "hero": {"displayName": ""}}
        match = {"id":match_id, "didRadiantWin":radiant_win, "rank":rank, "players" : players}


if __name__ == "__main__":
    #fetch_hero_picks(total_leagues_to_check=20, matches_per_league=100)
    fetch_heroId_to_name()

# {
#     "id": 8394100070,
#     "didRadiantWin": true,
#     "rank": 80,
#     "players": [
#       {
#         "isRadiant": true,
#         "heroId": 94,
#         "hero": {
#           "displayName": "Medusa"
#         }
#       },
#       {
#         "isRadiant": true,
#         "heroId": 84,
#         "hero": {
#           "displayName": "Ogre Magi"
#         }
#       },