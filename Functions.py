from pandas import DataFrame, set_option, concat
import matplotlib.pyplot as plt
import re
Qual_Stats_AVG = ["Pos", "Tm"]
Quant_Stats_AVG = ["Age", "G", "GS", "MP", "PTS", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P","2PA","2P%","eFG%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF"]
Quant_Stats_GL = ['Age','Result', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
Qual_Stats_GL = ['Tm', 'Away', 'Opp']
Stats_Requiring_Formatting =  ['Age','Result', 'GS', 'MP', 'FG', 'FGA', 'FG%','3P','3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']

def Graph_Averages_DF(d, players, stats = Quant_Stats_AVG):
    if len (players) > 1: _graph_averages_dfs(d, players, stats)
    else: _graph_averages_df(d, players, stats)
def Graph_Gamelog_Df(d, players, stats = Quant_Stats_GL):
    if len (players) > 1: _graph_gamelogs_dfs(d, players, stats)
    else: _graph_gamelogs_df(d, players, stats)
def Visualize_Spec_df(d, players, stats = Quant_Stats_AVG, to_list = False, stacked_bar = False):

    d = d[["Player"] + stats]                  # .. - shrink to stats (retain player to search their stats later)                          
    stat_df = _shrink_df(d, players, stats = stats.copy())

    return_stats = []
    num_players = len(players)                 # .. } Stats Setup
    if num_players > 1 and stacked_bar == False: fig, ax = plt.subplots(num_players, figsize=(15,3.5 * num_players))
    else: plt.figure(figsize=(15,3.5))

    for i in range(num_players):
        player_df = stat_df[stat_df['Player'] == players[i]]
        player_stats = _average_stats_from_df(player_df, stats)


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
def Live_Compare(d, stacked_bar = False):
    '''Description: Function allowing user to input names to then compare. 
    * d- df: data
    * stacked_bar- bool: overlay/separate player stat graphs'''
    selected = []
    players = d['Player'].values
    player = input("Which player's stats would you like to see? (' ' to terminate)")

    while player in players:
        selected.append(player)
        player = input("Which player's stats would you like to see? (' ' to terminate)")
    
    if len(selected) > 0: Visualize_Spec_df(d, selected, stacked_bar = stacked_bar)
    else: print("No players given!")
Display_Functions = [Graph_Averages_DF, Graph_Gamelog_Df, Live_Compare] # User functions driving data analysis

def _average_stats_from_dfs(d, players, stats) -> list:
    '''Returns list of multiple players' stats
    * d- df: data
    * players- list[str]: players
    * stats- list[str]: stats'''
    stat_df = _shrink_df(d, players, stats = stats.copy())
    return_stats = []
    for player in players:
        player_df = stat_df[stat_df['Player'] == player]   
        player_stats = _average_stats_from_df(player_df, stats)
        return_stats.append([player] + player_stats)
    return return_stats
def _average_stats_from_df(d, stats) -> list:
    '''Returns list of a single player's stats
    * d- df: data
    * stats- list[str]: stats'''
    player_stats = []
    for stat in stats:
        value = d[stat].iat[0]
        if "%" in stat: value *= 100
        if type(value) != str: value = round(value,2);player_stats.append(value)
    return player_stats
def _graph_averages_dfs(d, players, stats) -> None:
    '''Graph multiple players' stat averages   
    * d- df: data (season/career averages).
    * players- list(str): player(s).
    * stats- list (str): stats from d to visualize.'''                  
    np = len(players)
    stat_list = _average_stats_from_dfs(d, players, stats = stats.copy())
    fig, ax = plt.subplots(np, figsize=(15,3.5 * np))
    for set in stat_list:
        np -= 1
        player = set[0]
        vals = set[1:]
        ax[np].set_title(f"{player}'s stats:")
        b = ax[np].bar(x=stats, height=vals) ; ax[np].bar_label(b, vals)
def _graph_averages_df(d, player, stats) -> None:
    '''Graph a player's stat averages     
    * d- df: data (season/career averages).
    * players- list(str): player.
    * stats- list (str): stats from d to visualize.'''               
    stat_list = _average_stats_from_df(d, stats)
    plt.figure(figsize=(15,3.5)) ; plt.title(f"{player}'s stats:")
    b = plt.bar(x = stats, height = stat_list); plt.bar_label(b, stat_list)#if !to_list: (complete this if block if you want to_list to not also graph stats
def _graph_gamelogs_dfs(d, players, stats) -> None:
    '''Graph multiple players' gamelogs 
    * d- df: data (combined gamelogs).
    * players- list(str): player.
    * stats- list (str): stats from d to visualize.'''                 
    np = len(players)
    fig, ax = plt.subplots(np, figsize=(15,3.5 * np))
    games = list(d.index)
    for stat in stats:
        np -= 1
        player = players[np]
        player_df = d[d['Player'] == player]
        values = player_df[stat].values
        ax[np].set_title(f"{player}'s stats:")
        ax[np].scatter(x=stats, height=values, label=stat)
        ax[np].legend()
    plt.show()
def _graph_gamelogs_df(d, player, stats) -> None:
    '''Graph a single player's gamelogs   
    * d- df: data (gamelogs).
    * players- list(str): player.
    * stats- list (str): stats from d to visualize.'''
    
    plt.figure(figsize=(15,3.5)) ; plt.title(f"{player}'s gamelogs with selected stats: {stats}:")
    games = list(d.index)
    for stat in stats:
        values = d[stat].values
        if "%" in stat: values *= 100
        if type(values[0]) != bool and type(values[0]) != str: 
            values = values.round(decimals = 2)
            plt.scatter(x=games, y=values, label=stat)
    plt.legend()
    plt.show()
Helper_Functions = [_average_stats_from_dfs, _average_stats_from_df, _graph_averages_dfs, _graph_averages_df, _graph_gamelogs_df, _graph_gamelogs_dfs] # Factored out function code

def get_tags_from_dict(tag_dict, players) -> list: 
    '''Produce a list of player tags
    * league_tags- dict(str:str): dict {players:tags} in the NBA
    * players- list(str): list of players to produce tags of}'''
    return [tag_dict.get(player) for player in players]
def _shrink_df(d, players, stats = Quant_Stats_AVG) -> DataFrame:
    '''Shrink df to specified players, stats
    * d- df: data
    * players- list(str): player(s)
    * stats- list(str): stats from d to visualize'''
    if stats != None: #User specifies certain stats (non-default)
        stats = stats.copy()
        try: assert "Player" in stats #Makes sure that when we shrink the df to those stats, we don't accidentally remove the Player Name col (needed for compares)
        except AssertionError: stats.append("Player") 
        d = d[stats]
    d = d[d['Player'].isin(players)]
    return d
def _clean_html_gamelogs(d, season_stats = False) -> DataFrame:
    '''Cleans player gamelogs/season_stats
    * d- df: data (dirty gamelogs)
    * season_stats- bool: whether d is gamelogs or season averages'''
    set_option('mode.chained_assignment', None)
    d.dropna(subset=['Age'], inplace=True)
    d = d[d['Age'] != 'Age'] # = d[d["Rk"] != "Rk"] # Remove extra rows (there are rows that repeat the original column headers, but do not contain values (because the table is 80+ rows))
    if not season_stats: 
        d.rename(columns = {'Rk':'Game', 'G':'Played','Unnamed: 5':'Away', 'Unnamed: 7': 'Result'}, inplace = True) # rename column headers
        d.set_index('Game', inplace = True) # Set the game # as the index
        d['Away'].mask(d['Away'] == '@', True, inplace=True);d['Away'].fillna(value = False, inplace = True) # replace values in away column with bool
        d['Played'] = d['Played'].notna() # drop unplayed games
        d['Result'] = d['Result'].apply(lambda x: float(re.findall('\(([^)]*)\)', x)[0]))
        d = d[d.Played]
        d.reset_index(drop=True, inplace = True)
        d['Age'] = d['Age'].apply(lambda x: float(x[0:2]) + float(x[3:6])/365)
        d['MP'] = d["MP"].apply(lambda x: float(re.findall('([^:]*):(\d\d)', x)[0][0]) + float(re.findall('([^:]*):(\d\d)', x)[0][1])/60)
        for stat in Stats_Requiring_Formatting: d[stat] = d[stat].astype(float)
    return d
def _clean_html_career_stats(d) -> DataFrame:
    '''Description: Produce a cleaned DataFrame of a player's gamelogs/season_stats given a dirty DataFrame
    * d- df: data'''
    return _clean_html_gamelogs(d, season_stats = True)
def _combine_player_avgs(player1, player2) -> DataFrame: return concat([player1.get_career_averages(), player2.get_career_averages()])
def _combine_player_gamelogs(player1, player2) -> DataFrame: return concat([player1.get_gamelogs(), player2.get_gamelogs()])
Clean_Functions = [get_tags_from_dict, _shrink_df, _clean_html_gamelogs, _clean_html_career_stats, _combine_player_avgs, _combine_player_gamelogs] # Clean data and format
