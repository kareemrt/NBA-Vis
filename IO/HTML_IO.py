from bs4 import BeautifulSoup  # HTML IO: Methods for HTML data extraction for the NBA-vis program
from pandas import DataFrame, concat, read_html
from Functions import get_tags_from_dict, clean_gamelogs
import urllib.request as urlib
import re

def HTML_get_player_dict(roster_htmls) -> dict:
#   Description: Produce a team's player dict{names: tags} given roster url { roster_htmls- list(str): list of the html links for the roster tables on a team's basketball reference page. }
    player_tags = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z0-9]*)'

    for roster in roster_htmls:
        html_page = urlib.urlopen(roster)
        soup = BeautifulSoup(html_page, "html.parser")

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
    league_rosters = {}
    pattern = '/[a-zA-Z]*/([a-zA-Z]*)/'

    html_page = urlib.urlopen('https://www.basketball-reference.com/leagues/NBA_2023_standings.html')
    soup = BeautifulSoup(html_page, "html.parser")

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
def HTML_get_player_seasons(tag) -> list:
#   Description: Get the list of seasons a player has played. { player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
    df = read_html(f'https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game')[0].copy()
    df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
    return df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played
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

HTML_Functions = [HTML_get_player_dict, HTML_get_franchise_dict, HTML_get_player_seasons, HTML_get_combined_gamelogs, HTML_get_combined_career_stats]

def RAW_HTML_get_player_gamelogs(tag, season) -> DataFrame:
#   Description: Produce a DataFrame of a player's gamelogs for a given season. { player_tag- str: the user-specific id in basketball-reference.com links. 
#                                                                                 season- str: the season's year (2022-2023 season would be '2022'). }
    return read_html(f"https://www.basketball-reference.com/players/{tag[0]}/{tag}/gamelog/{season}#pgl_basic", match="Regular Season")[0].copy() # returns html tables list
def RAW_HTML_get_player_career_stats(tag) -> DataFrame: 
#   Description: Produce a DataFrame of a player's career averages. { player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
    return read_html(f"https://www.basketball-reference.com/players/{tag[0]}/{tag}.html#per_game")[0].copy()
def CLEAN_HTML_get_player_gamelogs(tag, seasons) -> DataFrame:
    df = []
    for season in seasons:
        try:
            gamelogs = RAW_HTML_get_player_gamelogs(tag, season)
            clean_df = clean_gamelogs(gamelogs)
            df.append(clean_df)
        except ValueError: print(f"{tag} has no gamelogs for the {season} season."); df.append(DataFrame())
    return concat(df)
def CLEAN_HTML_get_player_career_stats(tag) -> DataFrame:
    career_averages = RAW_HTML_get_player_career_stats(tag)
    clean_df = clean_gamelogs(career_averages, season_stats = True)
    return clean_df

HTML_Helper_Function = [RAW_HTML_get_player_career_stats, RAW_HTML_get_player_gamelogs, CLEAN_HTML_get_player_gamelogs, CLEAN_HTML_get_player_career_stats]
