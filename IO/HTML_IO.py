from Functions import get_tags_from_dict, clean_gamelogs
from File_IO import FileIO_Load_HTML_Credentials, FileIO_Load_HTML_Proxies
from pandas import DataFrame, concat, read_html
from bs4 import BeautifulSoup  # HTML IO: Methods for HTML data extraction for the NBA-vis program
from requests import get
from io import StringIO
import re
import random

user, passw, credentials = FileIO_Load_HTML_Credentials()
proxies = FileIO_Load_HTML_Proxies()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'}

def HTML_get_player_dict(roster_htmls) -> dict:
#   Description: Produce a team's player dict{names: tags} given roster url { roster_htmls- list(str): list of the html links for the roster tables on a team's basketball reference page. }
    player_tags = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z0-9]*)'

    for roster in roster_htmls:
        IP = random.choice(proxies)
        proxy = "socks5h://" + credentials + '@' + IP + ":1080" #;print(f"getting a team's player tag dictionary via the {IP} proxy!")
        html_page = -1
        while html_page == -1:
            try: html_page = get(roster, proxies={'http':proxy, 'https':proxy}, headers = headers, timeout=5)
            except: print(f"Connection Error to get player dict via proxy: {IP}"); pass
        soup = BeautifulSoup(html_page.text, "html.parser")

        for table in soup.findAll('table', attrs={'id': 'per_game'}):
            for tbody in table.findAll('tbody'):
                for tr in tbody.findAll('tr'):
                    for td in tr.findAll('td', attrs={'data-stat': ['player']}):
                        for a in td.findAll('a'):
                            player = a.text
                            link = a['href']
                            link = re.findall(pattern, link)[0]
                    player_tags[player] = link
    return player_tags
def HTML_get_franchise_dict(return_html = True) -> dict:
#   Description: Produce a league dict{teams: urls} for NBA teams { return_html- bool: return strings of either HTML or team tags (used in URL) }
    url = 'https://www.basketball-reference.com/leagues/NBA_2023_standings.html'
    IP = random.choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080" #;print(f"getting the league's team tag/url dictionary via the {IP} proxy!")
    html_page = -1
    while html_page == -1:
        try: html_page = get(url, proxies={'http':proxy, 'https':proxy})
        except: pass
    soup = BeautifulSoup(html_page.text, "html.parser")

    league_rosters = {}
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
                league_rosters[team] = team_link
    return league_rosters

HTML_League_Functions = [HTML_get_player_dict, HTML_get_franchise_dict]

def HTML_get_player_seasons(tag) -> list:
#   Description: Get the list of seasons a player has played. { player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
    url = f'http://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game'
    IP = random.choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    #print(f"getting {tag}'s season stats via the {IP} proxy!")
    r = -1
    while r == -1:
        try: r = get(url, proxies={'http':proxy, 'https':proxy})
        except: pass
    try: 
        df = read_html(StringIO(r.text))[0]
        df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
        seasons = df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played
    except ValueError: seasons = []
    return seasons
def HTML_get_combined_gamelogs(players, seasons, tag_dict) -> DataFrame:
#   Description: Produce a DataFrame of gamelogs for the given players over the given seasons. { players- list(str): list of players
#                                                                                                seasons- list(str): list of seasons 
#                                                                                                tag_dict- dict(str:str): dict{player:tag} }
    combined_logs = []
    multiple_players = len(players) > 1
    for player in players:
        tag = get_tags_from_dict(tag_dict, [player])[0]
        clean_df = CLEAN_HTML_get_player_gamelogs(tag, seasons)
        if multiple_players: clean_df['Player'] = player
        combined_logs.append(clean_df)
    return concat(combined_logs)
def HTML_get_combined_career_stats(players, tag_dict) -> DataFrame:
#   Description: Produce a DataFrame of career stats for the given players over the given seasons. { players- list(str): list of players
#                                                                                                    tag_dict- dict(str:str): dict{player:tag} }
    combined_stats = []
    multiple = len(players) > 1
    for player in players:
        player_tag = get_tags_from_dict(tag_dict, [player])[0]
        clean_df = CLEAN_HTML_get_player_career_stats(player_tag)
        if multiple: clean_df['Player'] = player
        combined_stats.append(clean_df)
    return concat(combined_stats)

HTML_Player_Functions = [HTML_get_player_seasons, HTML_get_combined_gamelogs, HTML_get_combined_career_stats]

def RAW_HTML_get_player_gamelogs(tag, season) -> DataFrame:
#   Description: Produce a DataFrame of a player's gamelogs for a given season. { player_tag- str: the user-specific id in basketball-reference.com links. 
#                                                                                 season- str: the season's year (2022-2023 season would be '2022'). }
    url = f"https://www.basketball-reference.com/players/{tag[0]}/{tag}/gamelog/{season}#pgl_basic"
    IP = random.choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    #print(f"getting {tag}'s gamelogs via the {IP} proxy!")
    r = -1
    while r == -1:
        try: r = get(url, proxies={'http':proxy, 'https':proxy})
        except: pass
    try: gamelogs = read_html(StringIO(r.text), match="Regular Season")[0] # returns html tables list
    except ValueError: gamelogs = DataFrame()
    return gamelogs
def RAW_HTML_get_player_career_stats(tag) -> DataFrame: 
#   Description: Produce a DataFrame of a player's career averages. { player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
    url = f"https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game"
    IP = random.choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    #print(f"getting {tag}'s gamelogs via the {IP} proxy!")
    r = -1
    while r == -1:
        try: r = get(url, proxies={'http':proxy, 'https':proxy})
        except: pass
    try: career_stats = read_html(StringIO(r.text))[0]
    except ValueError: career_stats = DataFrame()
    return career_stats
def CLEAN_HTML_get_player_gamelogs(tag, seasons) -> DataFrame:
    df = []
    for season in seasons:
        gamelogs = RAW_HTML_get_player_gamelogs(tag, season)
        if not gamelogs.empty: gamelogs = clean_gamelogs(gamelogs)
        df.append(gamelogs)
        #except ValueError: print(f"{tag} has no gamelogs for the {season} season."); df.append(DataFrame())
    return concat(df)
def CLEAN_HTML_get_player_career_stats(tag) -> DataFrame:
    career_averages = RAW_HTML_get_player_career_stats(tag)
    if not career_averages.empty: career_averages = clean_gamelogs(career_averages, season_stats = True)
    return career_averages

HTML_Helper_Function = [RAW_HTML_get_player_career_stats, RAW_HTML_get_player_gamelogs, CLEAN_HTML_get_player_gamelogs, CLEAN_HTML_get_player_career_stats]
