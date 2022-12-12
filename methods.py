# Name: Kareem T (github/kareemrt)
# Date: 12/11/2022
# Description: Abstracted methods from NBA visualization program
import matplotlib.pyplot as plt
import pandas as pd

Qual_Stats = ["Pos", "Tm"]
Quant_Stats = ["Age", "G", "GS", "MP", "PTS", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P","2PA","2P%","eFG%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF"]
All_Stats = Qual_Stats + Quant_Stats

def parse_player_df(d, players, stats = Quant_Stats.copy()):
    if stats != None: #User specifies certain stats (non-default)
        stats = stats.copy()
        try: assert "Player" in stats #Makes sure that when we shrink the df to those stats, we don't accidentally remove the Player Name col (needed for compares)
        except AssertionError: stats.append("Player") 
        d = d[stats]
    return d[d['Player'].isin(players)]
#   Description: Shrink df to specified players, stats.
#   Output: DataFrame
#   Input { 
#   d- df: data.
#   players- list(str): player(s).
#   stats- list(str): stats from d to visualize. } 
def Visualize_Stats(d, players, stats = Quant_Stats, to_list = False, stacked_bar = False):
    try: assert len(stats) > 0# Stats Setup - Ensure we don't accidentally remove the Player Name col (needed for compares) {
    except AssertionError: stats = ["PTS"] # .. 
    stats = stats.copy()
    d = d[["Player"] + stats]                  # .. - shrink to stats (retain player to search their stats later)                          # ..
    stat_df = parse_player_df(d, players, stats = stats)

    num_players = len(players)                 # .. } Stats Setup
    if num_players > 1 and stacked_bar == False: fig, ax = plt.subplots(num_players, figsize=(15,3.5 * num_players))
    else: plt.figure(figsize=(15,3.5))
    return_stats = []

    for i in range(num_players):
        player_df = stat_df[stat_df['Player'] == players[i]]   
        player_stats = []  

        for stat in stats:
            value = player_df[stat].iat[0]
            if "%" in stat: value *= 100
            if type(value) != str: value = round(value,2);player_stats.append(value)

        if stacked_bar:                 # If graph is stacked
            plt.title(f"{players} stat comparison:")
            b = plt.bar(x = stats, height = player_stats) ; plt.bar_label(b, player_stats) # Add player stats to the bars
        else:
            match num_players: # Non-stacked graph: Check how many players
                case 1: # 1 player : Use one graph
                    plt.title(f"{players[i]}'s stats:")
                    b = plt.bar(x = stats, height = player_stats) 
                    plt.bar_label(b, player_stats)#if !to_list: (complete this if block if you want to_list to not also graph stats
                case _: # 2+ players : Use 2+ graphs
                    ax[i].set_title(f"{players[i]}'s stats:")
                    b = ax[i].bar(x=stats, height=player_stats) ; ax[i].bar_label(b, player_stats)#if !to_list: (complete this if block if you want to_list to not also graph stats
        
        return_stats.append([players[i]] + player_stats) # Add player stats to all stats to return
    
    plt.legend(players)
    if to_list: return return_stats
#   Description: Graph the selected players stats as a dataframe, returns a list of those stats if specified.
#   Output: matplotlib graph AND/OR list(str/int)
#   Input {
#   d- df: data.
#   players- list(str): player(s).
#   stats- list (str): stats from d to visualize.
#   to_list- bool: returns a list of the visualized stats. If multiple players, returns a 2D list. }
#   
#   note: if 2D, each list indexes (e.g. Visualize_Stats()[0] vs Visualize_Stats[1]) players and sub-indexes (Vis_S[0][0] vs Vis_S[0][1]) are different stats for that player.
def Live_Compare(d, stacked_bar = False):
    selected = []
    players = d['Player'].values
    player = input("Which player's stats would you like to see? (' ' to terminate)")

    while player in players:
        selected.append(player)
        player = input("Which player's stats would you like to see? (' ' to terminate)")
    
    if len(selected) > 0: Visualize_Stats(d, selected, stacked_bar = stacked_bar)
    else: print("No players given!")
#   Description: Function allowing user to input names to then compare.
#   Output: matplotlib graph   
#   Input {
#   d- df: data.
#   stacked_bar- bool: whether the player stats should be overlayed or on separate graphs. }
def get_player_seasons_list(player_tag):
    df = pd.read_html(f'https://www.basketball-reference.com/players/{player_tag[0]}/{player_tag}.html#per_game')[0].copy()
    df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
    return df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played
#   Description: Get the list of seasons a player has played.
#   Output: list(str)
#   Input { 
#   player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
def get_player_career_stats(player_tag): return pd.read_html(f"https://www.basketball-reference.com/players/{player_tag[0]}/{player_tag}.html#per_game")[0].copy()
#   Description: Produce a DataFrame of a player's career averages.
#   Output: DataFrame
#   Input {
#   player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. }
def get_player_gamelogs(player_tag, season):
    return pd.read_html(f"https://www.basketball-reference.com/players/{player_tag[0]}/{player_tag}/gamelog/{season}#pgl_basic", match="Regular Season")[0].copy() # returns html tables list
#   Description: Produce a DataFrame of a player's gamelogs for a given season.
#   Output: DataFrame
#   Input {
#   player_tag- str: the user-specific id that is used in basketball-reference.com hyperlinks. 
#   season- str: the season's year (2022-2023 season would be '2022'). }
def clean_gamelogs(d):
    d = d.copy() # Copy the original df to avoid errors
    d = d[d["Rk"] != "Rk"] # Remove extra rows (there are rows that repeat the original column headers, but do not contain values (because the table is 80+ rows))
    d.rename(columns = {'Rk':'Game', 'G':'Played','Unnamed: 5':'Away', 'Unnamed: 7': 'Result'}, inplace = True) # rename column headers
    d.set_index('Game', inplace = True) # Set the game # as the index
    d['Away'].mask(d['Away'] == '@', True, inplace=True);d['Away'] = d['Away'].fillna(False) # replace values in away column with bool
    d.dropna(subset=['Played'], inplace=True) # drop unplayed games
    return d
#   Description: Produce a cleaned DataFrame of a player's gamelogs given a dirty DataFrame
#   Output: DataFrame
#   Input {
#   d- df: data. }
def pull_player_tags(roster_htmls):

    player_tags = {}
    pattern = '/[a-zA-Z]*/[a-zA-Z]/([a-zA-Z1-9]*)'

    for roster in roster_htmls:
        html_page = urllib.request.urlopen(roster)
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
#   Description: Produce a dictionary{player names: player tags} of players given a team's rosters (tags are unique ID's used for NBA athletes on BBREF.com)
#   Output: Dictionary
#   Input {
#   roster_htmls- list(str): list of the html links for the roster tables on a team's basketball reference page. }
def pull_league_tags(return_html = True):

    league_rosters = {}
    pattern = '/[a-zA-Z]*/([a-zA-Z]*)/'

    html_page = urllib.request.urlopen('https://www.basketball-reference.com/leagues/NBA_2023_standings.html')
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
#   Description: Produce a dictionary{team names: team htmls} of roster html pages for each team in the league, which helps pull user info.
#   Output: Dictionary
#   Input {
#   return_html- bool: set the type for the dictionary values to be HTML links, instead of str tags (like ones used for players). }
def get_player_tags(players): return [league_tags.get(key) for key in players]
#   Description: Produce a list of player tags given a list of players (tags are unique ID's used for NBA athletes on BBREF.com)
#   Output: List(str)
#   Input {
#   players- list(str): list of players to produce tags of. }
def produce_player_df(players, seasons):
    player_dfs = []
    multiple = len(players) > 1
    for player in players:
        player_tag = get_player_tags([player])[0]
        for season in seasons:
            season_games = get_player_gamelogs(player_tag, season)
            clean_df = clean_gamelogs(season_games)
            if multiple: clean_df['Player'] = player
            clean_df['Season'] = season
            player_dfs.append(clean_df)
    return pd.concat(player_dfs)
#   Description: Produce a DataFrame of gamelogs for the given players over the given seasons.
#   Output: DataFrame
#   Input {
#   players- list(str): list of players
#   seasons- list(str): list of seasons
#   }