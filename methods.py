Qual_Stats = ["Pos", "Tm"]
Quant_Stats = ["Age", "G", "GS", "MP", "PTS", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P","2PA","2P%","eFG%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF"]
All_Stats = Qual_Stats + Quant_Stats
import matplotlib.pyplot as plt
import pandas as pd

#Input: (d - df - data) , (players - list (str) - player(s)) , (stats - list (str) - stats to visualize from d)
def Get_Players_df(d, players, stats = Quant_Stats.copy()):
    if stats != None: #User specifies certain stats (non-default)
        stats = stats.copy()
        try: assert "Player" in stats #Makes sure that when we shrink the df to those stats, we don't accidentally remove the Player Name col (needed for compares)
        except AssertionError: stats.append("Player") 
        d = d[stats]
    return d[d['Player'].isin(players)]

#   Input:
#   stats - list (str) of stats to visualize from d
#   to_list - bool - returns a list of the visualized stats. If multiple players, returns a 2D list. 
#   if 2D, each list indexes (e.g. Visualize_Stats()[0] vs Visualize_Stats[1]) players and sub-indexes (Vis_S[0][0] vs Vis_S[0][1]) are different stats for that player

def Visualize_Stats(d, players, stats = Quant_Stats, to_list = False, stacked_bar = False):
    try: assert len(stats) > 0# Stats Setup - Ensure we don't accidentally remove the Player Name col (needed for compares) {
    except AssertionError: stats = ["PTS"] # .. 
    stats = stats.copy()
    d = d[["Player"] + stats]                  # .. - shrink to stats (retain player to search their stats later)                          # ..
    stat_df = Get_Players_df(d, players, stats = stats)

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
def Compare_Players(d, stacked_bar = False):
    selected = []
    players = d['Player'].values
    player = input("Which player's stats would you like to see? (' ' to terminate)")

    while player in players:
        selected.append(player)
        player = input("Which player's stats would you like to see? (' ' to terminate)")
    
    if len(selected) > 0: Visualize_Stats(d, selected, stacked_bar = stacked_bar)
    else: print("No players given!")
    
def get_seasons(player_html):
    df = pd.read_html(player_html)[0].copy()
    df.dropna(subset=['Age'], inplace=True) # drop unplayed seasons, which is just bloater rows
    return df['Season'].apply(lambda x: int(x[0:2] + x[5:7])).values # get the seasons he played

def get_gamelog_from_player_html(player_tag, season):
    return pd.read_html(f"https://www.basketball-reference.com/players/{player_tag[0]}/{player_tag}/gamelog/{season}#pgl_basic", match="Regular Season")[0].copy() # returns html tables list

def clean_season_df(d):
    d = d.copy() # Copy the original df to avoid errors
    d = d[d["Rk"] != "Rk"] # Remove extra rows (there are rows that repeat the original column headers, but do not contain values (because the table is 80+ rows))
    d.rename(columns = {'Rk':'Game', 'G':'Played','Unnamed: 5':'Away', 'Unnamed: 7': 'Result'}, inplace = True) # rename column headers
    d.set_index('Game', inplace = True) # Set the game # as the index
    d['Away'].mask(d['Away'] == '@', True, inplace=True);d['Away'] = d['Away'].fillna(False) # replace values in away column with bool
    d.dropna(subset=['Played'], inplace=True) # drop unplayed games
    return d

def get_roster(roster_html):

    team_players = []
    team_links = []

    html_page = urllib.request.urlopen(roster_html)
    soup = BeautifulSoup(html_page, "html.parser")

    for table in soup.findAll('table', attrs={'id': 'per_game'}):
        for tbody in table.findAll('tbody'):
            for tr in tbody.findAll('tr'):
                for td in tr.findAll('td', attrs={'data-stat': ['player']}):
                    for a in td.findAll('a'):
                        player_name = a.text
                        player_career_link = a['href']
                for td in tr.findAll('td', attrs={'data-stat': ['g']}):
                    for a in td.findAll('a'):
                        player_games_link = a['href']
                team_players.append(player_name)
                team_links.append((player_name, player_career_link, player_games_link))
    return team_players, team_links