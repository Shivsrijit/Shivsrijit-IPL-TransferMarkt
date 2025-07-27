import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPLScraper:
    def __init__(self):
        self.base_url = "https://www.iplt20.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_selenium()
    
    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def get_team_data(self):
        """Scrape team information from IPL website"""
        try:
            url = f"{self.base_url}/teams"
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "team-card"))
            )
            
            teams = []
            team_cards = self.driver.find_elements(By.CLASS_NAME, "team-card")
            
            for card in team_cards:
                team_data = {
                    'name': card.find_element(By.CLASS_NAME, "team-name").text,
                    'short_name': card.find_element(By.CLASS_NAME, "team-short-name").text,
                    'logo_url': card.find_element(By.TAG_NAME, "img").get_attribute("src"),
                    'home_ground': card.find_element(By.CLASS_NAME, "home-ground").text
                }
                teams.append(team_data)
            
            return teams
        except Exception as e:
            logger.error(f"Error scraping team data: {str(e)}")
            return []
    
    def get_player_data(self, team_url):
        """Scrape player information for a specific team"""
        try:
            self.driver.get(team_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "player-card"))
            )
            
            players = []
            player_cards = self.driver.find_elements(By.CLASS_NAME, "player-card")
            
            for card in player_cards:
                player_data = {
                    'name': card.find_element(By.CLASS_NAME, "player-name").text,
                    'role': card.find_element(By.CLASS_NAME, "player-role").text,
                    'nationality': card.find_element(By.CLASS_NAME, "player-nationality").text,
                    'batting_style': card.find_element(By.CLASS_NAME, "batting-style").text,
                    'bowling_style': card.find_element(By.CLASS_NAME, "bowling-style").text
                }
                players.append(player_data)
            
            return players
        except Exception as e:
            logger.error(f"Error scraping player data: {str(e)}")
            return []
    
    def get_match_data(self, season):
        """Scrape match information for a specific season"""
        try:
            url = f"{this.base_url}/matches/{season}"
            self.driver.get(url)
            WebDriverWait(this.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "match-card"))
            )
            
            matches = []
            match_cards = this.driver.find_elements(By.CLASS_NAME, "match-card")
            
            for card in match_cards:
                match_data = {
                    'date': card.find_element(By.CLASS_NAME, "match-date").text,
                    'venue': card.find_element(By.CLASS_NAME, "match-venue").text,
                    'team1': card.find_element(By.CLASS_NAME, "team1-name").text,
                    'team2': card.find_element(By.CLASS_NAME, "team2-name").text,
                    'result': card.find_element(By.CLASS_NAME, "match-result").text
                }
                matches.append(match_data)
            
            return matches
        except Exception as e:
            logger.error(f"Error scraping match data: {str(e)}")
            return []
    
    def get_player_stats(self, player_url):
        """Scrape detailed player statistics"""
        try:
            self.driver.get(player_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "player-stats"))
            )
            
            stats = {
                'batting': self._get_batting_stats(),
                'bowling': self._get_bowling_stats(),
                'fielding': self._get_fielding_stats()
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error scraping player stats: {str(e)}")
            return {}
    
    def _get_batting_stats(self):
        """Helper method to extract batting statistics"""
        try:
            batting_stats = {}
            stats_table = self.driver.find_element(By.CLASS_NAME, "batting-stats")
            rows = stats_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                batting_stats[cols[0].text] = {
                    'matches': cols[1].text,
                    'runs': cols[2].text,
                    'average': cols[3].text,
                    'strike_rate': cols[4].text
                }
            
            return batting_stats
        except Exception as e:
            logger.error(f"Error extracting batting stats: {str(e)}")
            return {}
    
    def _get_bowling_stats(self):
        """Helper method to extract bowling statistics"""
        try:
            bowling_stats = {}
            stats_table = self.driver.find_element(By.CLASS_NAME, "bowling-stats")
            rows = stats_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                bowling_stats[cols[0].text] = {
                    'matches': cols[1].text,
                    'wickets': cols[2].text,
                    'economy': cols[3].text,
                    'average': cols[4].text
                }
            
            return bowling_stats
        except Exception as e:
            logger.error(f"Error extracting bowling stats: {str(e)}")
            return {}
    
    def _get_fielding_stats(self):
        """Helper method to extract fielding statistics"""
        try:
            fielding_stats = {}
            stats_table = self.driver.find_element(By.CLASS_NAME, "fielding-stats")
            rows = stats_table.find_elements(By.TAG_NAME, "tr")
            
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                fielding_stats[cols[0].text] = {
                    'matches': cols[1].text,
                    'catches': cols[2].text,
                    'stumpings': cols[3].text,
                    'run_outs': cols[4].text
                }
            
            return fielding_stats
        except Exception as e:
            logger.error(f"Error extracting fielding stats: {str(e)}")
            return {}
    
    def close(self):
        """Close the Selenium WebDriver"""
        self.driver.quit()

if __name__ == "__main__":
    scraper = IPLScraper()
    try:
        # Example usage
        teams = scraper.get_team_data()
        print(f"Scraped {len(teams)} teams")
        
        for team in teams:
            players = scraper.get_player_data(team['url'])
            print(f"Scraped {len(players)} players for {team['name']}")
        
        matches = scraper.get_match_data(2023)
        print(f"Scraped {len(matches)} matches for season 2023")
        
    finally:
        scraper.close() 