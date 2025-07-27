import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from app.models.team import Team, Player
from app.models.match import Match, PlayerPerformance
from app import db
import random

class IPLScraper:
    def __init__(self):
        self.base_url = "https://www.cricbuzz.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def get_sample_data(self):
        """Return sample data for testing"""
        teams_data = [
            {
                'name': 'Chennai Super Kings',
                'short_name': 'CSK',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/CSK/logos/Roundbig/CSKroundbig.png',
                'home_ground': 'M. A. Chidambaram Stadium'
            },
            {
                'name': 'Mumbai Indians',
                'short_name': 'MI',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/MI/logos/Roundbig/MIroundbig.png',
                'home_ground': 'Wankhede Stadium'
            },
            {
                'name': 'Royal Challengers Bangalore',
                'short_name': 'RCB',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RCB/logos/Roundbig/RCBroundbig.png',
                'home_ground': 'M. Chinnaswamy Stadium'
            }
        ]
        
        players_data = [
            {
                'name': 'MS Dhoni',
                'team_name': 'Chennai Super Kings',
                'role': 'Wicket Keeper',
                'nationality': 'Indian',
                'batting_style': 'Right Handed',
                'bowling_style': 'N/A'
            },
            {
                'name': 'Rohit Sharma',
                'team_name': 'Mumbai Indians',
                'role': 'Batsman',
                'nationality': 'Indian',
                'batting_style': 'Right Handed',
                'bowling_style': 'Right Arm Off Break'
            },
            {
                'name': 'Virat Kohli',
                'team_name': 'Royal Challengers Bangalore',
                'role': 'Batsman',
                'nationality': 'Indian',
                'batting_style': 'Right Handed',
                'bowling_style': 'Right Arm Medium'
            }
        ]
        
        matches_data = [
            {
                'team1_name': 'Chennai Super Kings',
                'team2_name': 'Mumbai Indians',
                'team1_score': '192/4',
                'team2_score': '195/4',
                'venue': 'M. A. Chidambaram Stadium',
                'match_date': datetime(2024, 3, 23),
                'season': 2024
            },
            {
                'team1_name': 'Royal Challengers Bangalore',
                'team2_name': 'Chennai Super Kings',
                'team1_score': '173/6',
                'team2_score': '176/4',
                'venue': 'M. Chinnaswamy Stadium',
                'match_date': datetime(2024, 3, 25),
                'season': 2024
            }
        ]
        
        return teams_data, players_data, matches_data

    def scrape_teams(self):
        """Scrape team information"""
        try:
            response = requests.get(f"{self.base_url}/cricket-series/ipl-2024/teams", headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            teams_data = []
            team_elements = soup.find_all('div', class_='cb-series-matches')
            
            for team in team_elements:
                name = team.find('h3').text.strip()
                short_name = name.split()[0][:3].upper()
                logo_url = team.find('img')['src'] if team.find('img') else ''
                home_ground = team.find('div', class_='venue').text.strip() if team.find('div', class_='venue') else 'TBD'
                
                team_data = {
                    'name': name,
                    'short_name': short_name,
                    'logo_url': logo_url,
                    'home_ground': home_ground
                }
                teams_data.append(team_data)
            
            return teams_data if teams_data else self.get_sample_data()[0]
        except Exception as e:
            print(f"Error scraping teams: {str(e)}")
            return self.get_sample_data()[0]

    def scrape_matches(self, season=2024):
        """Scrape match information"""
        try:
            response = requests.get(f"{self.base_url}/cricket-series/ipl-2024/matches", headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            matches_data = []
            match_elements = soup.find_all('div', class_='cb-mtch-lst')
            
            for match in match_elements:
                teams = match.find_all('div', class_='cb-mtch-tm')
                team1_name = teams[0].text.strip() if len(teams) > 0 else "TBD"
                team2_name = teams[1].text.strip() if len(teams) > 1 else "TBD"
                
                scores = match.find_all('div', class_='cb-scr-wrp')
                team1_score = scores[0].text.strip() if len(scores) > 0 else "N/A"
                team2_score = scores[1].text.strip() if len(scores) > 1 else "N/A"
                
                venue = match.find('div', class_='cb-mtch-ven').text.strip() if match.find('div', class_='cb-mtch-ven') else "TBD"
                match_date = match.find('div', class_='cb-mtch-dt').text.strip() if match.find('div', class_='cb-mtch-dt') else datetime.now().strftime('%d %b %Y')
                
                match_data = {
                    'team1_name': team1_name,
                    'team2_name': team2_name,
                    'team1_score': team1_score,
                    'team2_score': team2_score,
                    'venue': venue,
                    'match_date': datetime.strptime(match_date, '%d %b %Y'),
                    'season': season
                }
                matches_data.append(match_data)
            
            return matches_data if matches_data else self.get_sample_data()[2]
        except Exception as e:
            print(f"Error scraping matches: {str(e)}")
            return self.get_sample_data()[2]

    def scrape_players(self):
        """Scrape player information"""
        try:
            response = requests.get(f"{self.base_url}/cricket-series/ipl-2024/players", headers=self.headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            players_data = []
            player_elements = soup.find_all('div', class_='cb-player-card')
            
            for player in player_elements:
                name = player.find('h3').text.strip()
                team_name = player.find('div', class_='team').text.strip() if player.find('div', class_='team') else "TBD"
                role = player.find('div', class_='role').text.strip() if player.find('div', class_='role') else "TBD"
                nationality = player.find('div', class_='nationality').text.strip() if player.find('div', class_='nationality') else "TBD"
                
                stats = player.find_all('div', class_='stat')
                batting_style = stats[0].text.strip() if len(stats) > 0 else "N/A"
                bowling_style = stats[1].text.strip() if len(stats) > 1 else "N/A"
                
                player_data = {
                    'name': name,
                    'team_name': team_name,
                    'role': role,
                    'nationality': nationality,
                    'batting_style': batting_style,
                    'bowling_style': bowling_style
                }
                players_data.append(player_data)
            
            return players_data if players_data else self.get_sample_data()[1]
        except Exception as e:
            print(f"Error scraping players: {str(e)}")
            return self.get_sample_data()[1]

class IPLDataGenerator:
    def __init__(self):
        self.teams = [
            {
                'name': 'Chennai Super Kings',
                'short_name': 'CSK',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/CSK/logos/Roundbig/CSKroundbig.png',
                'home_ground': 'M. A. Chidambaram Stadium'
            },
            {
                'name': 'Mumbai Indians',
                'short_name': 'MI',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/MI/logos/Roundbig/MIroundbig.png',
                'home_ground': 'Wankhede Stadium'
            },
            {
                'name': 'Royal Challengers Bangalore',
                'short_name': 'RCB',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RCB/logos/Roundbig/RCBroundbig.png',
                'home_ground': 'M. Chinnaswamy Stadium'
            },
            {
                'name': 'Kolkata Knight Riders',
                'short_name': 'KKR',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/KKR/logos/Roundbig/KKRroundbig.png',
                'home_ground': 'Eden Gardens'
            },
            {
                'name': 'Rajasthan Royals',
                'short_name': 'RR',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/RR/logos/Roundbig/RRroundbig.png',
                'home_ground': 'Sawai Mansingh Stadium'
            },
            {
                'name': 'Delhi Capitals',
                'short_name': 'DC',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/DC/logos/Roundbig/DCroundbig.png',
                'home_ground': 'Arun Jaitley Stadium'
            },
            {
                'name': 'Sunrisers Hyderabad',
                'short_name': 'SRH',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/SRH/logos/Roundbig/SRHroundbig.png',
                'home_ground': 'Rajiv Gandhi International Stadium'
            },
            {
                'name': 'Punjab Kings',
                'short_name': 'PBKS',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/PBKS/logos/Roundbig/PBKSroundbig.png',
                'home_ground': 'Punjab Cricket Association Stadium'
            },
            {
                'name': 'Gujarat Titans',
                'short_name': 'GT',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/GT/logos/Roundbig/GTroundbig.png',
                'home_ground': 'Narendra Modi Stadium'
            },
            {
                'name': 'Lucknow Super Giants',
                'short_name': 'LSG',
                'logo_url': 'https://bcciplayerimages.s3.ap-south-1.amazonaws.com/ipl/LSG/logos/Roundbig/LSGroundbig.png',
                'home_ground': 'Ekana Cricket Stadium'
            }
        ]
        
        self.player_names = {
            'CSK': ['MS Dhoni', 'Ruturaj Gaikwad', 'Ravindra Jadeja', 'Moeen Ali', 'Deepak Chahar', 'Shivam Dube', 'Ajinkya Rahane', 'Tushar Deshpande', 'Matheesha Pathirana', 'Maheesh Theekshana'],
            'MI': ['Rohit Sharma', 'Suryakumar Yadav', 'Jasprit Bumrah', 'Hardik Pandya', 'Ishan Kishan', 'Tilak Varma', 'Tim David', 'Piyush Chawla', 'Jason Behrendorff', 'Kumar Kartikeya'],
            'RCB': ['Virat Kohli', 'Faf du Plessis', 'Glenn Maxwell', 'Mohammed Siraj', 'Dinesh Karthik', 'Rajat Patidar', 'Wanindu Hasaranga', 'Josh Hazlewood', 'Harshal Patel', 'Shahbaz Ahmed'],
            'KKR': ['Shreyas Iyer', 'Andre Russell', 'Sunil Narine', 'Nitish Rana', 'Varun Chakravarthy', 'Venkatesh Iyer', 'Shardul Thakur', 'Rinku Singh', 'Umesh Yadav', 'Lockie Ferguson'],
            'RR': ['Sanju Samson', 'Jos Buttler', 'Yuzvendra Chahal', 'Ravichandran Ashwin', 'Yashasvi Jaiswal', 'Trent Boult', 'Shimron Hetmyer', 'Prasidh Krishna', 'Devdutt Padikkal', 'Riyan Parag'],
            'DC': ['Rishabh Pant', 'David Warner', 'Axar Patel', 'Prithvi Shaw', 'Anrich Nortje', 'Mitchell Marsh', 'Kuldeep Yadav', 'Lalit Yadav', 'Khaleel Ahmed', 'Rovman Powell'],
            'SRH': ['Aiden Markram', 'Bhuvneshwar Kumar', 'Mayank Agarwal', 'Rahul Tripathi', 'Washington Sundar', 'Umran Malik', 'T Natarajan', 'Abhishek Sharma', 'Heinrich Klaasen', 'Marco Jansen'],
            'PBKS': ['Shikhar Dhawan', 'Kagiso Rabada', 'Arshdeep Singh', 'Liam Livingstone', 'Sam Curran', 'Rahul Chahar', 'Harpreet Brar', 'Jitesh Sharma', 'Prabhsimran Singh', 'Nathan Ellis'],
            'GT': ['Hardik Pandya', 'Shubman Gill', 'Rashid Khan', 'Mohammed Shami', 'David Miller', 'Rahul Tewatia', 'Wriddhiman Saha', 'Alzarri Joseph', 'Sai Sudharsan', 'Joshua Little'],
            'LSG': ['KL Rahul', 'Quinton de Kock', 'Marcus Stoinis', 'Ravi Bishnoi', 'Krunal Pandya', 'Avesh Khan', 'Deepak Hooda', 'Kyle Mayers', 'Mark Wood', 'Ayush Badoni']
        }
        
        self.player_roles = ['Batsman', 'Bowler', 'All-rounder', 'Wicket Keeper']
        self.nationalities = ['Indian', 'Australian', 'South African', 'English', 'West Indian', 'New Zealander', 'Bangladeshi', 'Afghan']
        self.batting_styles = ['Right Handed', 'Left Handed']
        self.bowling_styles = ['Right Arm Fast', 'Right Arm Medium', 'Right Arm Off Break', 'Left Arm Fast', 'Left Arm Orthodox', 'Leg Break', 'N/A']
        
        self.venues = [
            'M. A. Chidambaram Stadium',
            'Wankhede Stadium',
            'M. Chinnaswamy Stadium',
            'Eden Gardens',
            'Sawai Mansingh Stadium',
            'Arun Jaitley Stadium',
            'Rajiv Gandhi International Stadium',
            'Punjab Cricket Association Stadium',
            'Narendra Modi Stadium',
            'Ekana Cricket Stadium'
        ]
    
    def generate_teams(self, count=10):
        """Generate sample teams"""
        return self.teams[:count]
    
    def generate_players(self, count=100):
        """Generate sample players with real names"""
        players = []
        for team in self.teams:
            team_short_name = team['short_name']
            team_players = self.player_names.get(team_short_name, [])
            
            for player_name in team_players:
                player = {
                    'name': player_name,
                    'team_name': team['name'],
                    'role': random.choice(self.player_roles),
                    'nationality': random.choice(self.nationalities),
                    'batting_style': random.choice(self.batting_styles),
                    'bowling_style': random.choice(self.bowling_styles)
                }
                players.append(player)
        
        # If we need more players, generate random ones
        while len(players) < count:
            team = random.choice(self.teams)
            player = {
                'name': f'Player {len(players) + 1}',
                'team_name': team['name'],
                'role': random.choice(self.player_roles),
                'nationality': random.choice(self.nationalities),
                'batting_style': random.choice(self.batting_styles),
                'bowling_style': random.choice(self.bowling_styles)
            }
            players.append(player)
        
        return players
    
    def generate_matches(self, count=100):
        """Generate sample matches"""
        matches = []
        start_date = datetime(2022, 3, 1)
        
        for i in range(count):
            # Generate a random date between 2022 and 2024
            match_date = start_date + timedelta(days=random.randint(0, 730))
            
            # Select two different teams
            team1, team2 = random.sample(self.teams, 2)
            
            # Generate random scores
            team1_runs = random.randint(120, 220)
            team1_wickets = random.randint(0, 10)
            team2_runs = random.randint(120, 220)
            team2_wickets = random.randint(0, 10)
            
            match = {
                'team1_name': team1['name'],
                'team2_name': team2['name'],
                'team1_score': f'{team1_runs}/{team1_wickets}',
                'team2_score': f'{team2_runs}/{team2_wickets}',
                'venue': random.choice(self.venues),
                'match_date': match_date,
                'season': match_date.year
            }
            matches.append(match)
        
        return matches
    
    def generate_player_performances(self, count=100):
        """Generate sample player performances"""
        performances = []
        for i in range(count):
            # Select a random player
            player = random.choice(self.generate_players(1))
            
            # Generate random performance stats
            runs = random.randint(0, 150)
            wickets = random.randint(0, 5)
            catches = random.randint(0, 3)
            
            performance = {
                'player_name': player['name'],
                'team_name': player['team_name'],
                'runs': runs,
                'wickets': wickets,
                'catches': catches
            }
            performances.append(performance)
        
        return performances

def populate_database():
    """Populate the database with generated sample data"""
    generator = IPLDataGenerator()
    
    try:
        # Clear existing data
        db.session.query(PlayerPerformance).delete()
        db.session.query(Match).delete()
        db.session.query(Player).delete()
        db.session.query(Team).delete()
        db.session.commit()
        
        # Generate and add teams
        teams_data = generator.generate_teams(10)
        team_objects = {}
        for team_data in teams_data:
            team = Team(**team_data)
            db.session.add(team)
            db.session.flush()  # Get the ID without committing
            team_objects[team_data['name']] = team
        
        # Generate and add players
        players_data = generator.generate_players(100)
        for player_data in players_data:
            team_name = player_data.pop('team_name')
            team = team_objects.get(team_name)
            if team:
                player = Player(team_id=team.id, **player_data)
                db.session.add(player)
        
        # Generate and add matches
        matches_data = generator.generate_matches(100)
        for match_data in matches_data:
            team1_name = match_data.pop('team1_name')
            team2_name = match_data.pop('team2_name')
            
            team1 = team_objects.get(team1_name)
            team2 = team_objects.get(team2_name)
            
            if team1 and team2:
                match = Match(
                    team1_id=team1.id,
                    team2_id=team2.id,
                    **match_data
                )
                db.session.add(match)
        
        # Generate and add player performances
        performances_data = generator.generate_player_performances(100)
        for perf_data in performances_data:
            player_name = perf_data.pop('player_name')
            team_name = perf_data.pop('team_name')
            
            team = team_objects.get(team_name)
            if team:
                player = Player.query.filter_by(name=player_name, team_id=team.id).first()
                if player:
                    match = Match.query.order_by(db.func.random()).first()
                    if match:
                        performance = PlayerPerformance(
                            player_id=player.id,
                            match_id=match.id,
                            **perf_data
                        )
                        db.session.add(performance)
        
        db.session.commit()
        print("Database populated successfully with 100 instances of sample data!")
    except Exception as e:
        db.session.rollback()
        print(f"Error populating database: {str(e)}")
        raise 