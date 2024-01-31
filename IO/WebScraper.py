# Name : WebScraper.py
# Auth : KT
# Desc : Module that webscrapes Basketball Reference and returns DataFrames
from bs4 import BeautifulSoup  # bs4 : HTML processing
import pandas as pd            # pd  : dataframe creation
import os                      # os  : env variables
import re                      # re  : str pattern procesing
import io                      # io  : HTTP req processing
#import URLProxyC as mylib     # URLP: *CUSTOM* my own lib - wraps Socks5 proxy (credentials loaded in 'credentials.json')

UseProxy = os.environ.get('USE_PROXY') == "1"
if UseProxy: import URLProxy as req
else: import requests as req

REFORMAT =  ['Age','Result', 'GS', 'MP', 'FG', 'FGA', 'FG%','3P','3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
REFORMATCS =  ['Age','G', 'GS', 'MP', 'FG', 'FGA', 'FG%','3P','3PA', '3P%', '2P', '2PA', '2P%', 'eFG%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

def Get_Players(team, season = 2023) -> dict:
    '''Returns a dict {PLAYER name, bbref PLAYER tag} given a [list of team urls]'''

    # Type checks
    assert (type(team) == str and type(season) == int)

    # Get HTML
    players = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z0-9]*)'
    r = req.get(f'https://www.basketball-reference.com/teams/{team}/{season}.html#roster')
    if not UseProxy: r = r.text
    soup = BeautifulSoup(r, "lxml")
    # HTML Parsing
    for table in soup.findAll('table', {'id': 'roster'}):
        for tbody in table.findAll('tbody'):
            for tr in tbody.findAll('tr'):
                for td in tr.findAll('td', attrs={'data-stat': ['player']}):
                    for a in td.findAll('a'):
                        player = a.text
                        ptag = a['href']
                        ptag = re.findall(pattern, ptag)[0]
                players[player] = ptag
        break
    return players

def Get_Teams(season = 2023) -> list:
    '''Returns a list [(tag, team), (tag2, team2),...]'''

    # Type checks
    assert type(season) == int

    # Get raw html (requires a fix)
    r = req.get(url=f'https://www.basketball-reference.com/leagues/NBA_{season}_standings.html#expanded_standings')
    if not UseProxy: r = r.text
    page = r.replace('<!--', '') # (the fix)
    soup = BeautifulSoup(page, features="html.parser")
    pattern = '/[a-zA-Z]*/([a-zA-Z]*)/'
    teams = []

    # Parse html
    for table in soup.findAll('table', attrs={'id': ['expanded_standings']}, recursive=True):
        for tbody in table.findAll('tbody'):
            for tr in tbody.findAll('tr'):
                for td in tr.findAll('td', attrs={'data-stat': ['team_name']}):
                    for a in td.findAll('a'):
                        team = a.text
                        tag = a['href']
                        tag = re.findall(pattern, tag)[0]
                teams.append((tag, team))
    return teams

def Get_Seasons(tag) -> list:
    '''Return a [list of player seasons]'''
    r = req.get(url=f'http://www.basketball-reference.com/players/{tag[0]}/{tag}.html#totals')
    if not UseProxy: r = r.text
    try:     # HTML Parsing
        df = pd.read_html(io.StringIO(r))[1]
        if('Age' not in df.columns): 
            df = pd.read_html(io.StringIO(r))[0]
            if('Age' not in df.columns): df = pd.read_html(io.StringIO(r))[2]
        df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons (bloater rows)
        seasons = df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # Convert (yyyy-yyyy) format to (yyyy)
    except ValueError: seasons = []
    finally:       
        return seasons

def Get_Gamelogs(player, tag, season, playoffs = False) -> pd.DataFrame:
    '''Return DataFrame of gamelogs given a [list of players] and [list of seasons]'''

    # Get HTML
    url=f"https://www.basketball-reference.com/players/{tag[0]}/{tag}/gamelog/{season}#pgl_basic"
    if playoffs: url += '_playoffs'
    r = req.get(url)
    if not UseProxy: r = r.text

    # Parse HTML
    try: 
        logs = pd.read_html(io.StringIO(r), match='Regular Season')[0] # returns html tables list
        logs['Season'] = season
        logs['Player'] = player
        logs['Playoffs'] = int(playoffs)
    except ValueError as e: 
        print(f'WebScraper.py: Get_Gamelogs (Value error): {e}')
        logs = pd.DataFrame()
    finally: 
        r.close()
        return Clean_DF(logs)

def Get_Career(player, tag) -> pd.DataFrame: 
    '''Return DataFrame of career averages given a [list of players]'''

    # Get HTML
    r = req.get(url=f"https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game")
    if not UseProxy: r = r.text

    try: 

        # Find the proper 'career stats' table
        cs = pd.read_html(io.StringIO(r))[1]
        if 'Age' not in cs.columns: 
            cs =  pd.read_html(io.StringIO(r))[0]
            if 'Age' not in cs.columns: 
                cs =  pd.read_html(io.StringIO(r))[2]
        # Mark player
        cs['Player'] = player
        cs['Tag'] = tag
        r.close()
        return Clean_DF(cs, career = True)
    
    except ValueError as e: 
        print(f'WebScraper.py: Get_Career (Value error): {e}')
        r.close()
        return pd.DataFrame()

def Get_Playoffs(season) -> pd.DataFrame:
    '''Return DataFrame of playoff teams given a season'''
    url=f'https://www.basketball-reference.com/playoffs/NBA_{season}.html#per_game-team'
    # Get HTML
    r = req.get(url)
    if not UseProxy: r = r.text
    #print(html_page)
    # Read HTML info / close connection
    try: 
        tables = pd.read_html(io.StringIO(r))
        for table in tables: 
            if 'Team' not in table.columns and 'Tm' not in table.columns: continue
            try: teams = table['Team'][:-1].values
            except ValueError and KeyError: teams = table['Tm'][:-1].values
            assert len(teams) in [8, 10, 12, 16, 20]
            return teams
    except ValueError as e: 
        print(f'WebScraper.py: Get_Playoffs (Value error): {e}')
        return []


def Clean_DF(d, career = False) -> pd.DataFrame:
    '''Cleans player gamelogs, [optional] clean season_stats'''
    d.dropna(subset=['Age'], inplace=True) # Drop rows that don't have data values
    d = d[d['Age'] != 'Age']               # Remove extra rows (there are rows that repeat the original column headers w/o values)
    d = d[pd.to_numeric(d['PTS'], errors='coerce').notnull()]
    if not career: 
        d.rename(columns = {'Rk':'Game', 'G':'Played','Unnamed: 5':'Away', 'Unnamed: 7': 'Result'}, inplace = True) # Rename columns
        d.set_index('Game', inplace = True)                                                                         # Set game # as index
        d['Away'].mask(d['Away'] == '@', True, inplace=True);d['Away'].fillna(value = False, inplace = True)        # convert Away column -> bool
        d['Played'] = d['Played'].notna()                                                                           # get unplayed games
        d['Result'] = d['Result'].apply(lambda x: float(re.findall('\(([^)]*)\)', x)[0]))                           # parse game result (from text)
        d = d[d.Played]                                                                                             # drop unplayed games
        d.reset_index(drop=True, inplace = True)                                                                    # reset index after game drop
        d['Age'] = d['Age'].apply(lambda x: float(x[0:2]) + float(x[3:6])/365)                                      # convert age to float
        d['MP'] = d["MP"].apply(lambda x: float(re.findall('([^:]*):(\d\d)', x)[0][0]) + float(re.findall('([^:]*):(\d\d)', x)[0][1])/60) # convert minutes to float
        d = d.drop('Played', axis=1)                                                                                # drop unplayed games column
        for stat in REFORMAT: d[stat] = d[stat].astype(float)                                                       # reformat to floats
    else:
        d = d[d['Season'] != 'Career']
        d['Season'] = d['Season'].apply(lambda x: 2000 + int(x[-2:]))
        for stat in REFORMATCS: d[stat] = d[stat].astype(float)
    return d

