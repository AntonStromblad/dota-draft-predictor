import cloudscraper
import json
import time
import os
import requests

STRATZ_TOKEN = "KEY"
file_path = "raw_data/pro_picks.json"


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
    return all_matches


def fetch_heroId_to_name():
    response = requests.get("https://api.opendota.com/api/heroes",[])
    heroes_data = response.json()

    hero_dict = {hero["id"]: hero["localized_name"] for hero in heroes_data}

    return hero_dict

def fetch_hero_picks_normal_matches(id_to_hero :dict):
    all_matches = []
    response = requests.get("https://api.opendota.com/api/publicMatches", params={"min_rank" : 80}).json()
    matches = response.json()
    for match in matches:
        match = {}
        match_id = response.get("match_id",0)
        radiant_win = response.get("radiant_win", True)
        rank = response.get("avg_rank_tier", 75)
        radiant_team = response.get("radiant_team", [])
        dire_team = response.get("dire_team", [])
        players = []
        for hero_id in radiant_team:
            players.append({"isRadiant": True, "heroId":hero_id, "hero": {"displayName": f"{id_to_hero[hero_id]}"}})

        for hero_id in dire_team:
            players.append({"isRadiant": False, "heroId":hero_id, "hero": {"displayName": f"{id_to_hero[hero_id]}"}})

        match = {"id":match_id, "didRadiantWin":radiant_win, "rank":rank, "players" : players}
        all_matches.append(match)
    
    print(all_matches)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_matches, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    new_matches = []
    #form_pro_leagues = fetch_hero_picks(total_leagues_to_check=20, matches_per_league=100)
    #new_matches.extend(form_pro_leagues)

    dictionary = fetch_heroId_to_name()
    from_normal = fetch_hero_picks_normal_matches(dictionary)
    new_matches.extend(from_normal)

    with open(file_path, "r", encoding="utf-8") as f:
        gamla_matcher = json.load(f)
        gamla_matcher.extend(new_matches)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(gamla_matcher, f, indent=2, ensure_ascii=False)