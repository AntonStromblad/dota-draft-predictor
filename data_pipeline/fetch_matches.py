import cloudscraper
import json
import time
import os

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
                league_name = league.get('displayName', 'Okänd Liga')
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
        

if __name__ == "__main__":
    fetch_hero_picks(total_leagues_to_check=20, matches_per_league=100)
