from bs4 import BeautifulSoup  # HTML IO: Methods for HTML data extraction for the NBA-vis program
from time import sleep
from random import choice
from re import findall
from requests import Session, get
from io import StringIO
from pandas import DataFrame, concat, read_html
from Functions import get_tags_from_dict, _clean_html_gamelogs
import IO.File_IO as IO
user, passw, credentials = IO.FileIO_Load_HTML_Credentials()
proxies = IO.FileIO_Load_HTML_Proxies()
headers = IO.FileIO_Load_HTML_Headers()
s = Session()
def HTML_get_player_dict(roster_htmls) -> dict:
#   Description: Produce a team's player dict{names: tags} given roster url { roster_htmls- list(str): list of the html links for the roster tables on a team's basketball reference page. }
    player_tags = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z0-9]*)'

    for roster in roster_htmls:
        IP = choice(proxies)
        proxy = "socks5h://" + credentials + '@' + IP + ":1080" #;print(f"getting a team's player tag dictionary via the {IP} proxy!")
        agent = choice(headers)
        html_page = -1
        while html_page == -1:
            try: html_page = s.get(roster, proxies={'http':proxy, 'https':proxy}, headers = {'User-Agent':agent}, timeout=5)
            except Exception as e:print(e); print(f"Connection Error to get player dict via proxy: {IP}"); pass
        soup = BeautifulSoup(html_page.text, "lxml")

        for table in soup.findAll('table', attrs={'id': 'per_game'}):
            for tbody in table.findAll('tbody'):
                for tr in tbody.findAll('tr'):
                    for td in tr.findAll('td', attrs={'data-stat': ['player']}):
                        for a in td.findAll('a'):
                            player = a.text
                            link = a['href']
                            link = findall(pattern, link)[0]
                    player_tags[player] = link
    return player_tags
def HTML_get_franchise_dict(return_html = True) -> dict:
#   Description: Produce a league dict{teams: urls} for NBA teams { return_html- bool: return strings of either HTML or team tags (used in URL) }
    url = 'https://www.basketball-reference.com/leagues/NBA_2023_standings.html'
    IP = choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080" #;print(f"getting the league's team tag/url dictionary via the {IP} proxy!")
    html_page = -1
    while html_page == -1:
        try: html_page = s.get(url, proxies={'http':proxy, 'https':proxy})
        except: pass
    soup = BeautifulSoup(html_page.text, "lxml")

    league_rosters = {}
    pattern = '/[a-zA-Z]*/([a-zA-Z]*)/'

    for table in soup.findAll('table', attrs={'id': ['confs_standings_E', 'confs_standings_W']}):
        for tbody in table.findAll('tbody'):
            for tr in tbody.findAll('tr'):
                for th in tr.findAll('th', attrs={'data-stat': ['team_name']}):
                    for a in th.findAll('a'):
                        team = a.text
                        team_link = a['href']
                        team_link = findall(pattern, team_link)[0]
                        if return_html: team_link = f'https://www.basketball-reference.com/teams/{team_link}/2023.html#roster'
                league_rosters[team] = team_link
    return league_rosters
League_Functions = [HTML_get_player_dict, HTML_get_franchise_dict]

def HTML_get_player_seasons(tag) -> list:
#   Description: Get the list of seasons a player has played. { player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
    url = f'http://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game'
    IP = choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    #print(f"getting {tag}'s season stats via the {IP} proxy!")
    r = -1
    while r == -1:
        try: r = s.get(url, proxies={'http':proxy, 'https':proxy}, timeout=10)
        except Exception as e: print(e); sleep(5); pass
    try: 
        df = read_html(StringIO(r.text))[0]
        df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
        seasons = df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played
    except ValueError: seasons = []
    r.close()
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
Player_Functions = [HTML_get_player_seasons, HTML_get_combined_gamelogs, HTML_get_combined_career_stats]

def RAW_HTML_get_player_gamelogs(tag, season) -> DataFrame:
#   Description: Produce a DataFrame of a player's gamelogs for a given season. { player_tag- str: the user-specific id in basketball-reference.com links. 
#                                                                                 season- str: the season's year (2022-2023 season would be '2022'). }
    url = f"https://www.basketball-reference.com/players/{tag[0]}/{tag}/gamelog/{season}#pgl_basic"
    IP = choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    #print(f"getting {tag}'s gamelogs via the {IP} proxy!")
    r = -1
    while r == -1:
        try: r = s.get(url, proxies={'http':proxy, 'https':proxy}, timeout=10)
        except Exception as e: print(e); sleep(5); pass
    try: gamelogs = read_html(StringIO(r.text), match="Regular Season")[0] # returns html tables list
    except ValueError: gamelogs = DataFrame()
    r.close()
    return gamelogs
def RAW_HTML_get_player_career_stats(tag) -> DataFrame: 
#   Description: Produce a DataFrame of a player's career averages. { player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
    url = f"https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game"
    IP = choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    #print(f"getting {tag}'s gamelogs via the {IP} proxy!")
    r = -1
    while r == -1:
        try: r = s.get(url, proxies={'http':proxy, 'https':proxy}, timeout=10)
        except Exception as e: print(e); sleep(5); pass
    try: career_stats = read_html(StringIO(r.text))[0]
    except ValueError: career_stats = DataFrame()
    r.close()
    return career_stats
def CLEAN_HTML_get_player_gamelogs(tag, seasons) -> DataFrame:
    df = []
    valid = False
    for season in seasons:
        gamelogs = RAW_HTML_get_player_gamelogs(tag, season)
        if not gamelogs.empty: 
            gamelogs = _clean_html_gamelogs(gamelogs)
            gamelogs['Season'] = season
            valid = True
        df.append(gamelogs)
        sleep(2)
        #except ValueError: print(f"{tag} has no gamelogs for the {season} season."); df.append(DataFrame())
    if valid: cleaned_logs = concat(df).reset_index(drop=True)
    else: cleaned_logs = DataFrame()
    return cleaned_logs
def CLEAN_HTML_get_player_career_stats(tag) -> DataFrame:
    career_averages = RAW_HTML_get_player_career_stats(tag)
    if not career_averages.empty: career_averages = _clean_html_gamelogs(career_averages, season_stats = True)
    return career_averages
Helper_Functions = [RAW_HTML_get_player_career_stats, RAW_HTML_get_player_gamelogs, CLEAN_HTML_get_player_gamelogs, CLEAN_HTML_get_player_career_stats]
