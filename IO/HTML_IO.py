from bs4 import BeautifulSoup  # HTML IO: Methods for HTML data extraction for the NBA-vis program
from time import sleep
from random import choice
from re import findall
from requests import Session
from io import StringIO
from pandas import DataFrame, concat, read_html
from Functions import _clean_html
import IO.File_IO as IO
import logging

user, passw, credentials, proxies, headers = IO.FileIO_HTML()
tags = IO.FileIO_Load_PlayersD()
s = Session()
logging.basicConfig(level = logging.WARNING, filename='Logs/network_logs.log', format='%(asctime)s - %(levelname)s - %(message)s')
NETLOG = logging.Logger("NETLOG")

def HTML_player_tags(roster_htmls) -> dict:
    '''Returns a dict {PLAYER name, bbref PLAYER tag} given a [list of team urls]'''
    player_tags = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z0-9]*)'
    for roster in roster_htmls:
        # URL Connection
        IP = choice(proxies)
        proxy = "socks5h://" + credentials + '@' + IP + ":1080"
        agent = choice(headers)
        # Request
        html_page = -1
        while html_page == -1:
            try: html_page = s.get(roster, proxies={'http':proxy, 'https':proxy}, headers = {'User-Agent':agent}, timeout=5)
            except Exception: 
                NETLOG.warning(f"Connection Error to get player dict via proxy: {IP}")
                IP, agent = choice(proxies), choice(headers)
                proxy = "socks5h://" + credentials + '@' + IP + ":1080"; sleep(0.5); pass
        soup = BeautifulSoup(html_page.text, "lxml")
        # HTML Parsing
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

def HTML_team_urls(return_html = True) -> dict:
    '''Returns a dict {TEAM name, bbref TEAM tag}, [optional] return html links as dict values'''
    url = 'https://www.basketball-reference.com/leagues/NBA_2023_standings.html'
    IP = choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080" #;print(f"getting the league's team tag/url dictionary via the {IP} proxy!")
    html_page = -1
    while html_page == -1:
        try: html_page = s.get(url, proxies={'http':proxy, 'https':proxy})
        except Exception:
            NETLOG.warning(f"Connection Error to get team urls via proxy: {IP}")
            IP, agent = choice(proxies), choice(headers)
            proxy = "socks5h://" + credentials + '@' + IP + ":1080"; sleep(0.5); pass
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

def HTML_seasons(player) -> list:
    '''Return a [list of player seasons]'''
    # URL Connection
    tag = tags[player]
    url, IP = f'http://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game', choice(proxies)
    proxy = "socks5h://" + credentials + "@" + IP + ":1080"
    # Request
    r = -1
    while r == -1:
        try: r = s.get(url, proxies={'http':proxy, 'https':proxy}, timeout=10)
        except Exception: 
            NETLOG.warning(f"Connection Error to get player seasons via proxy: {IP}")
            IP, agent = choice(proxies), choice(headers)
            proxy = "socks5h://" + credentials + '@' + IP + ":1080"; sleep(0.5); pass
    # HTML Parsing
    try: 
        df = read_html(StringIO(r.text))[0]
        df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
        seasons = df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played
    except ValueError: seasons = []
    r.close()
    return seasons

def HTML_gamelogs(players, seasons) -> DataFrame:
    '''Return DataFrame of gamelogs given a [list of players] and [list of seasons]'''
    gamelogs = DataFrame()
    if type(players) is str: players = [players]
    for player in players:
        tag = tags[player]
        for season in seasons:
            # Establish URL connection
            url, IP = f"https://www.basketball-reference.com/players/{tag[0]}/{tag}/gamelog/{season}#pgl_basic", choice(proxies)
            proxy = "socks5h://" + credentials + "@" + IP + ":1080"
            r = -1
            while r == -1:
                try: r = s.get(url, proxies={'http':proxy, 'https':proxy}, timeout=10)
                except Exception:
                    NETLOG.warning(f"Connection Error to get player gamelogs via proxy: {IP}")
                    IP, agent = choice(proxies), choice(headers)
                    proxy = "socks5h://" + credentials + '@' + IP + ":1080"; sleep(0.5); pass
            # Read HTML info / close connection
            try: playerlogs = read_html(StringIO(r.text), match="Regular Season")[0] # returns html tables list
            except ValueError: playerlogs = DataFrame()
            r.close()
            # Add DF
            playerlogs['Season'] = season
            playerlogs['Player'] = player
            if not playerlogs.empty: gamelogs = concat([gamelogs,playerlogs]).reset_index(drop=True)
    return _clean_html(gamelogs) if not gamelogs.empty else gamelogs

def HTML_career_stats(players) -> DataFrame: 
    '''Return DataFrame of career averages given a [list of players]'''
    career = DataFrame()
    if type(players) is str: players = [players]
    for player in players:
        # Establish URL connection
        tag = tags[player]
        url, IP = f"https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game", choice(proxies)
        proxy = "socks5h://" + credentials + "@" + IP + ":1080"
        r = -1
        while r == -1:
            try: r = s.get(url, proxies={'http':proxy, 'https':proxy}, timeout=10)
            except Exception:
                NETLOG.warning(f"Connection Error to get player career stats via proxy: {IP}")
                IP, agent = choice(proxies), choice(headers)
                proxy = "socks5h://" + credentials + '@' + IP + ":1080"; sleep(0.5); pass
        # Read HTML info / close connection
        try: career_stats = read_html(StringIO(r.text))[0]
        except ValueError as e: print(e); career_stats = DataFrame()
        r.close()
        career_stats['Player'] = player
        if not career_stats.empty: career = concat([career,career_stats]).reset_index(drop=True)
    return _clean_html(career, season_stats=True) if not career.empty else career
