# Name : WebScraper.py
# Auth : KT
# Desc : Module that webscrapes Basketball Reference and returns DataFrames
from bs4 import BeautifulSoup  # bs4 : HTML data processing
import pandas as pd            # pd  : create dataframes from data
import re                      # re  : string pattern procesing
import io                      # io  : parse url requests
import time
import URLProxy                # URLP: *CUSTOM* my own wheel that wraps Socks5 proxy (credentials loaded in 'credentials.json' on the requests.get() method

def Get_Players(teams) -> dict:
    '''Returns a dict {PLAYER name, bbref PLAYER tag} given a [list of team urls]'''
    players = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z0-9]*)'
    for team, url in teams.items():
        # Request
        html_page = URLProxy.force_connect(url)
        soup = BeautifulSoup(html_page.text, "lxml")
        # HTML Parsing
        for table in soup.findAll('table', attrs={'id': 'per_game'}):
            for tbody in table.findAll('tbody'):
                for tr in tbody.findAll('tr'):
                    for td in tr.findAll('td', attrs={'data-stat': ['player']}):
                        for a in td.findAll('a'):
                            player = a.text
                            link = a['href']
                            link = re.findall(pattern, link)[0]
                    players[player] = (link, team)
    return players

def Get_Teams(return_html = True) -> dict:
    '''Returns a dict {TEAM name, bbref TEAM tag}, [optional] return html links as dict values'''
    html_page = URLProxy.force_connect(url='https://www.basketball-reference.com/leagues/NBA_2023_standings.html')
    soup = BeautifulSoup(html_page.text, "lxml")
    teams = {}
    pattern = '/[a-zA-Z]*/([a-zA-Z]*)/'
    for table in soup.findAll('table', attrs={'id': ['confs_standings_E', 'confs_standings_W']}):
        for tbody in table.findAll('tbody'):
            for tr in tbody.findAll('tr'):
                for th in tr.findAll('th', attrs={'data-stat': ['team_name']}):
                    for a in th.findAll('a'):
                        team = a.text
                        team_link = a['href']
                        team_link = re.findall(pattern, team_link)[0]
                        if return_html: team_link = f'https://www.basketball-reference.com/teams/{team_link}/2023.html#roster'
                teams[team] = team_link
    return teams

def Get_Seasons(tag) -> list:
    '''Return a [list of player seasons]'''
    # URL Connection
    r = URLProxy.force_connect(url=f'http://www.basketball-reference.com/players/{tag[0]}/{tag}.html#totals')
    # HTML Parsing
    try: 
        df = pd.read_html(io.StringIO(r.text))[1]
        if('Age' not in df.columns): df = pd.read_html(io.StringIO(r.text))[0]
        df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
        seasons = df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played
    except ValueError: seasons = []
    r.close()
    return seasons

def Get_Gamelogs(player, tag, seasons) -> pd.DataFrame:
    '''Return DataFrame of gamelogs given a [list of players] and [list of seasons]'''
    gamelogs = pd.DataFrame()
    for season in seasons:
        # Establish URL connection
        r = URLProxy.force_connect(url=f"https://www.basketball-reference.com/players/{tag[0]}/{tag}/gamelog/{season}#pgl_basic")
        # Read HTML info / close connection
        try: playerlogs = pd.read_html(io.StringIO(r.text), match="Regular Season")[0] # returns html tables list
        except ValueError: playerlogs = pd.DataFrame()
        r.close()
        # Add DF
        playerlogs['Season'] = season
        playerlogs['Player'] = player
        if not playerlogs.empty: gamelogs = pd.concat([gamelogs,playerlogs]).reset_index(drop=True)
        time.sleep(0.5)
    return Clean_DF(gamelogs)

def Get_Career(player, tag) -> pd.DataFrame: 
    '''Return DataFrame of career averages given a [list of players]'''
    # Establish URL connection
    r = URLProxy.force_connect(url=f"https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game")
    # Read HTML info / close connection
    try: 
        career_stats = pd.read_html(io.StringIO(r.text))[1]
        if 'Age' not in career_stats.columns: career_stats =  pd.read_html(io.StringIO(r.text))[0]
        career_stats['Player'] = player
    except ValueError as e: print(e); career_stats = pd.DataFrame()
    r.close()
    return Clean_DF(career_stats, career = True)

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