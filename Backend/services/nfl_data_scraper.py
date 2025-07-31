"""
NFL Data Scraper for Pro Football Reference
Handles web scraping of player statistics and information
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import Dict, List, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NFLDataScraper:
    """Scraper for Pro Football Reference data"""
    
    BASE_URL = "https://www.pro-football-reference.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def _make_request(self, url: str, delay: float = 1.0) -> Optional[BeautifulSoup]:
        """Make a request with rate limiting and error handling"""
        try:
            time.sleep(delay)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            return None
            
    def get_active_players_list(self, position: str = None) -> List[Dict]:
        """Get list of active NFL players"""
        players = []
        
        # Get players by team
        teams_url = f"{self.BASE_URL}/teams/"
        soup = self._make_request(teams_url)
        
        if not soup:
            return players
            
        # Find team links (simplified approach)
        team_links = soup.find_all('a', href=re.compile(r'/teams/[a-z]{3}/2024\.htm'))
        
        for team_link in team_links[:3]:  # Limit to first 3 teams for testing
            team_url = self.BASE_URL + team_link.get('href')
            team_soup = self._make_request(team_url)
            
            if team_soup:
                players.extend(self._parse_team_roster(team_soup, team_link.get('href')))
                
        return players
    
    def _parse_team_roster(self, soup: BeautifulSoup, team_href: str) -> List[Dict]:
        """Parse team roster from team page"""
        players = []
        team_abbr = team_href.split('/')[2]
        
        # Find roster table
        roster_table = soup.find('table', {'id': 'roster'})
        if not roster_table:
            return players
            
        rows = roster_table.find('tbody').find_all('tr') if roster_table.find('tbody') else []
        
        for row in rows:
            try:
                player_data = self._parse_player_row(row, team_abbr)
                if player_data:
                    players.append(player_data)
            except Exception as e:
                logger.error(f"Error parsing player row: {e}")
                continue
                
        return players
        
    def _parse_player_row(self, row, team_abbr: str) -> Optional[Dict]:
        """Parse individual player row from roster table"""
        cells = row.find_all(['td', 'th'])
        if len(cells) < 6:
            return None
            
        try:
            # Extract player link and ID
            player_link = cells[1].find('a')
            if not player_link:
                return None
                
            player_href = player_link.get('href', '')
            player_name = player_link.text.strip()
            
            # Extract PFR ID from href (e.g., '/players/A/AdamDa01.htm' -> 'AdamDa01')
            pfr_id_match = re.search(r'/players/\w/(\w+)\.htm', player_href)
            pfr_id = pfr_id_match.group(1) if pfr_id_match else None
            
            return {
                'pfr_id': pfr_id,
                'name': player_name,
                'position': cells[2].text.strip() if len(cells) > 2 else '',
                'current_team': team_abbr,
                'jersey_number': cells[0].text.strip() if cells[0].text.strip().isdigit() else None,
                'age': int(cells[3].text.strip()) if len(cells) > 3 and cells[3].text.strip().isdigit() else None,
                'height': cells[4].text.strip() if len(cells) > 4 else '',
                'weight': int(cells[5].text.strip()) if len(cells) > 5 and cells[5].text.strip().isdigit() else None,
                'college': cells[6].text.strip() if len(cells) > 6 else '',
                'player_url': self.BASE_URL + player_href if player_href else None
            }
        except Exception as e:
            logger.error(f"Error extracting player data: {e}")
            return None
            
    def get_player_season_stats(self, pfr_id: str, years: List[int] = None) -> List[Dict]:
        """Get season-by-season stats for a player"""
        if not years:
            years = list(range(2020, 2025))  # Last 5 seasons
            
        player_url = f"{self.BASE_URL}/players/{pfr_id[0]}/{pfr_id}.htm"
        soup = self._make_request(player_url)
        
        if not soup:
            return []
            
        stats = []
        
        # Look for passing stats table
        passing_table = soup.find('table', {'id': 'passing'})
        if passing_table:
            stats.extend(self._parse_passing_stats(passing_table, pfr_id))
            
        # Look for rushing stats table
        rushing_table = soup.find('table', {'id': 'rushing_and_receiving'})
        if rushing_table:
            stats.extend(self._parse_rushing_receiving_stats(rushing_table, pfr_id))
            
        # Look for defense stats table
        defense_table = soup.find('table', {'id': 'defense'})
        if defense_table:
            stats.extend(self._parse_defense_stats(defense_table, pfr_id))
            
        return stats
        
    def _parse_passing_stats(self, table, pfr_id: str) -> List[Dict]:
        """Parse passing statistics table"""
        stats = []
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 10:
                continue
                
            try:
                year_cell = cells[0]
                if not year_cell.text.strip().isdigit():
                    continue
                    
                season_year = int(year_cell.text.strip())
                
                stats.append({
                    'pfr_id': pfr_id,
                    'season_year': season_year,
                    'team': cells[1].text.strip(),
                    'position': 'QB',
                    'age': int(cells[2].text.strip()) if cells[2].text.strip().isdigit() else None,
                    'games_played': int(cells[3].text.strip()) if cells[3].text.strip().isdigit() else 0,
                    'games_started': int(cells[4].text.strip()) if cells[4].text.strip().isdigit() else 0,
                    'pass_completions': int(cells[7].text.strip()) if cells[7].text.strip().isdigit() else 0,
                    'pass_attempts': int(cells[8].text.strip()) if cells[8].text.strip().isdigit() else 0,
                    'pass_yards': int(cells[10].text.strip()) if cells[10].text.strip().isdigit() else 0,
                    'pass_touchdowns': int(cells[11].text.strip()) if cells[11].text.strip().isdigit() else 0,
                    'interceptions': int(cells[12].text.strip()) if cells[12].text.strip().isdigit() else 0,
                    'qb_rating': float(cells[15].text.strip()) if cells[15].text.strip() and cells[15].text.strip() != '' else 0.0,
                })
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing passing stats row: {e}")
                continue
                
        return stats
        
    def _parse_rushing_receiving_stats(self, table, pfr_id: str) -> List[Dict]:
        """Parse rushing and receiving statistics table"""
        stats = []
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 15:
                continue
                
            try:
                year_cell = cells[0]
                if not year_cell.text.strip().isdigit():
                    continue
                    
                season_year = int(year_cell.text.strip())
                
                stats.append({
                    'pfr_id': pfr_id,
                    'season_year': season_year,
                    'team': cells[1].text.strip(),
                    'age': int(cells[2].text.strip()) if cells[2].text.strip().isdigit() else None,
                    'games_played': int(cells[3].text.strip()) if cells[3].text.strip().isdigit() else 0,
                    'games_started': int(cells[4].text.strip()) if cells[4].text.strip().isdigit() else 0,
                    'rush_attempts': int(cells[5].text.strip()) if cells[5].text.strip().isdigit() else 0,
                    'rush_yards': int(cells[6].text.strip()) if cells[6].text.strip().isdigit() else 0,
                    'rush_touchdowns': int(cells[7].text.strip()) if cells[7].text.strip().isdigit() else 0,
                    'receptions': int(cells[9].text.strip()) if cells[9].text.strip().isdigit() else 0,
                    'receiving_yards': int(cells[10].text.strip()) if cells[10].text.strip().isdigit() else 0,
                    'receiving_touchdowns': int(cells[11].text.strip()) if cells[11].text.strip().isdigit() else 0,
                })
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing rushing/receiving stats row: {e}")
                continue
                
        return stats
        
    def _parse_defense_stats(self, table, pfr_id: str) -> List[Dict]:
        """Parse defensive statistics table"""
        stats = []
        rows = table.find('tbody').find_all('tr') if table.find('tbody') else []
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 15:
                continue
                
            try:
                year_cell = cells[0]
                if not year_cell.text.strip().isdigit():
                    continue
                    
                season_year = int(year_cell.text.strip())
                
                stats.append({
                    'pfr_id': pfr_id,
                    'season_year': season_year,
                    'team': cells[1].text.strip(),
                    'age': int(cells[2].text.strip()) if cells[2].text.strip().isdigit() else None,
                    'games_played': int(cells[3].text.strip()) if cells[3].text.strip().isdigit() else 0,
                    'games_started': int(cells[4].text.strip()) if cells[4].text.strip().isdigit() else 0,
                    'tackles_total': int(cells[5].text.strip()) if cells[5].text.strip().isdigit() else 0,
                    'tackles_solo': int(cells[6].text.strip()) if cells[6].text.strip().isdigit() else 0,
                    'tackles_assists': int(cells[7].text.strip()) if cells[7].text.strip().isdigit() else 0,
                    'sacks': float(cells[8].text.strip()) if cells[8].text.strip() and cells[8].text.strip() != '' else 0.0,
                    'def_interceptions': int(cells[10].text.strip()) if cells[10].text.strip().isdigit() else 0,
                    'forced_fumbles': int(cells[13].text.strip()) if cells[13].text.strip().isdigit() else 0,
                    'fumble_recoveries': int(cells[14].text.strip()) if cells[14].text.strip().isdigit() else 0,
                })
            except (ValueError, IndexError) as e:
                logger.error(f"Error parsing defense stats row: {e}")
                continue
                
        return stats
        
    def get_nfl_teams(self) -> List[Dict]:
        """Get list of all NFL teams"""
        teams = []
        teams_url = f"{self.BASE_URL}/teams/"
        soup = self._make_request(teams_url)
        
        if not soup:
            return teams
            
        # Parse team information from the teams page
        team_links = soup.find_all('a', href=re.compile(r'/teams/[a-z]{3}/$'))
        
        for link in team_links:
            team_name = link.text.strip()
            team_abbr = link.get('href').split('/')[2]
            
            teams.append({
                'name': team_name,
                'abbreviation': team_abbr,
                'city': team_name.rsplit(' ', 1)[0] if ' ' in team_name else team_name,
            })
            
        return teams