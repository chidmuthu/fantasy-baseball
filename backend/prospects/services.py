import requests
import time
import logging
from typing import Dict, Optional
import io
import zipfile
import re
from difflib import get_close_matches
import pandas as pd
from pybaseball import batting_stats_range, pitching_stats_range
from datetime import date

logger = logging.getLogger(__name__)


class BaseballDataService:
    """Service for fetching baseball statistics from external sources using Chadwick Bureau lookup"""
    
    def __init__(self):
        self.chadwick_url = "https://github.com/chadwickbureau/register/archive/refs/heads/master.zip"
        self._chadwick_data = None
    
    def _extract_people_files(self, zip_archive: zipfile.ZipFile):
        """Extract all people.csv files from the zip archive"""
        people_pattern = re.compile("/people.+csv$")
        return [
            zip_info for zip_info in zip_archive.infolist()
            if people_pattern.search(zip_info.filename)
        ]
    
    def load_chadwick_data(self):
        """Load Chadwick Bureau player data from zip file (MLB players only)"""
        if self._chadwick_data is not None:
            return self._chadwick_data
            
        try:
            logger.info("Loading Chadwick Bureau player data from zip...")
            response = requests.get(self.chadwick_url)
            response.raise_for_status()
            
            # Extract all people.csv files from the zip
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                people_files = self._extract_people_files(zip_file)
                
                if not people_files:
                    logger.error("Could not find any people.csv files in the zip")
                    return []
                
                logger.info(f"Found {len(people_files)} people.csv files")
                
                # Read all CSV files and combine them
                all_players = []
                for file_info in people_files:
                    logger.info(f"Reading {file_info.filename}")
                    with zip_file.open(file_info.filename) as csv_file:
                        df = pd.read_csv(csv_file, low_memory=False)
                        
                        # Filter for MLB players only (those with key_mlbam)
                        mlb_df = df[df['key_mlbam'].notna() & (df['key_mlbam'] != '')]
                        
                        # Convert to list of dictionaries
                        for _, row in mlb_df.iterrows():
                            all_players.append({
                                'name_first': str(row.get('name_first', '')).lower(),
                                'name_last': str(row.get('name_last', '')).lower(),
                                'key_mlbam': int(row.get('key_mlbam', '')),
                                'birth_year': row.get('birth_year'),
                                'birth_month': row.get('birth_month'),
                                'birth_day': row.get('birth_day')
                            })
                
                self._chadwick_data = all_players
                logger.info(f"Loaded {len(self._chadwick_data)} MLB players from Chadwick Bureau")
                return self._chadwick_data
            
        except Exception as e:
            logger.error(f"Error loading Chadwick Bureau data: {e}")
            return []
    
    def find_player_mlb_id(self, player_name: str, players: pd.DataFrame, birth_year: Optional[int] = None, 
                            birth_month: Optional[int] = None, birth_day: Optional[int] = None) -> Optional[str]:
        """
        Find Baseball Reference ID for a player using Chadwick Bureau data
        
        Args:
            player_name: Full name of the player (e.g., "Mike Trout")
            birth_year: Player's birth year (optional, for more accurate matching)
            birth_month: Player's birth month (optional, for more accurate matching)
            birth_day: Player's birth day (optional, for more accurate matching)
            
        Returns:
            int MLB Player ID (e.g., 545361) or None if not found
        """
        try:
            if not players:
                return None
            
            # Split player name into first and last
            name_parts = player_name.strip().split()
            if len(name_parts) < 2:
                logger.warning(f"Player name '{player_name}' doesn't have enough parts")
                return None
            
            first_name = name_parts[0].lower()
            last_name = name_parts[-1].lower()
            
            logger.info(f"Searching for player: {first_name} {last_name}")
            if birth_year:
                logger.info(f"With birth year: {birth_year}")
            
            # Search for exact name match first
            exact_matches = []
            for player in players:
                if player['name_first'] == first_name and player['name_last'] == last_name:
                    exact_matches.append(player)
            
            if exact_matches:
                # If we have birthday info, try to match by birthday
                if birth_year and len(exact_matches) > 1:
                    for player in exact_matches:
                        if (player['birth_year'] == birth_year and 
                            (not birth_month or player['birth_month'] == birth_month) and
                            (not birth_day or player['birth_day'] == birth_day)):
                            mlb_id = player['key_mlbam']
                            logger.info(f"Found exact match with birthday: {mlb_id}")
                            return mlb_id
                
                # If no birthday match or only one exact name match, return the first
                mlb_id = exact_matches[0]['key_mlbam']
                logger.info(f"Found exact name match: {mlb_id}")
                return mlb_id
            
            # If no exact match, try fuzzy matching
            all_names = [f"{p['name_first']} {p['name_last']}" for p in players]
            search_name = f"{first_name} {last_name}"
            
            matches = get_close_matches(search_name, all_names, n=5, cutoff=0.6)
            
            if matches:
                logger.info(f"Found fuzzy matches: {matches}")
                
                # If we have birthday info, try to find the best match using birthday
                if birth_year:
                    best_match = None
                    best_score = 0
                    
                    for match in matches:
                        match_first, match_last = match.split(' ', 1)
                        for player in players:
                            if player['name_first'] == match_first and player['name_last'] == match_last:
                                # Calculate birthday match score
                                score = 0
                                if player['birth_year'] == birth_year:
                                    score += 3  # Year match is most important
                                if birth_month and player['birth_month'] == birth_month:
                                    score += 2  # Month match is second most important
                                if birth_day and player['birth_day'] == birth_day:
                                    score += 1  # Day match is least important
                                
                                if score > best_score:
                                    best_score = score
                                    best_match = player
                    
                    if best_match and best_score > 0:
                        mlb_id = best_match['key_mlbam']
                        logger.info(f"Using fuzzy match with birthday (score {best_score}): {mlb_id}")
                        return mlb_id
                
                # If no birthday match or no birthday provided, return the first fuzzy match
                for match in matches:
                    match_first, match_last = match.split(' ', 1)
                    for player in players:
                        if player['name_first'] == match_first and player['name_last'] == match_last:
                            mlb_id = player['key_mlbam']
                            logger.info(f"Using fuzzy match (no birthday): {mlb_id}")
                            return mlb_id
            
            logger.warning(f"No match found for player: {player_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error finding player ID for {player_name}: {e}")
            return None
    
    def get_player_stats_by_id(self, mlb_id: int, pitching: bool = False) -> Optional[float]:
        """
        Get player stats using Baseball Reference ID
        
        Args:
            mlb_id: MLB Player ID (e.g., 545361)
            pitching: Whether to get pitching stats (default is False)
        Returns:
            Count of either at bats or innings pitched
        """
        try:
            if pitching:
                return self._get_innings_pitched(mlb_id)
            else:
                return self._get_at_bats(mlb_id)
        except Exception as e:
            logger.error(f"Error getting player stats for {mlb_id}: {e}")
            return None
    
    def _get_innings_pitched(self, mlb_id: int) -> Optional[float]:
        """
        Get innings pitched for a player
        """
        logger.info(f"Getting innings pitched for {mlb_id}")
        stats = pitching_stats_range('2022-05-01', date.today().strftime('%Y-%m-%d'))
        return stats[stats['mlbID'].astype(int) == mlb_id]['IP'].iloc[0]
    
    
    def _get_at_bats(self, mlb_id: int) -> Optional[float]:
        """
        Get at bats for a player
        """
        stats = batting_stats_range('2022-05-01', date.today().strftime('%Y-%m-%d'))
        return stats[stats['mlbID'].astype(int) == mlb_id]['AB'].iloc[0]
    
    def search_player(self, player_name: str, players: pd.DataFrame, birth_year: Optional[int] = None,
                     birth_month: Optional[int] = None, birth_day: Optional[int] = None, pitching: bool = False) -> Optional[float]:
        """
        Search for a player using Chadwick Bureau lookup
        
        Args:
            player_name: Full name of the player
            birth_year: Player's birth year (optional, for more accurate matching)
            birth_month: Player's birth month (optional, for more accurate matching)
            birth_day: Player's birth day (optional, for more accurate matching)
            pitching: Whether to get pitching stats (default is False)
            
        Returns:
            Count of either at bats or innings pitched as float
        """
        try:
            # Find the Baseball Reference ID
            mlb_id = self.find_player_mlb_id(player_name, players, birth_year, birth_month, birth_day)
            if not mlb_id:
                logger.warning(f"Could not find Baseball Reference ID for: {player_name}")
                return None
            
            # Get player stats using the ID
            return self.get_player_stats_by_id(mlb_id, pitching)
            
        except Exception as e:
            logger.error(f"Error searching for player {player_name}: {e}")
            return None
    
    
    def get_mlb_appearances(self, player_name: str, players: pd.DataFrame, pitching: bool = False) -> Optional[float]:
        """
        Get MLB-only appearances (at bats or innings pitched) for a player
        
        Args:
            player_name: Full name of the player
            pitching: Whether to get pitching stats (default is False)
        Returns:
            Count of either at bats or innings pitched as float
        """
        try:
            # Rate limiting
            time.sleep(5)
            
            player_data = self.search_player(player_name, players, pitching=pitching)
            if not player_data:
                return None
            
            logger.info(f"Found MLB-only stats for {player_name}: {player_data} AB or IP")
            return player_data
            
            
        except Exception as e:
            logger.error(f"Error getting MLB appearances for {player_name}: {e}")
            return None
    



# Simple factory function - just use the web scraping service
def get_baseball_data_service():
    """Get the baseball data service"""
    return BaseballDataService() 