from pandas import DataFrame, set_option, concat
import matplotlib.pyplot as plt
import re

set_option('mode.chained_assignment', None)

QN_AVG = ["Age", "G", "GS", "MP", "PTS", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P","2PA","2P%","eFG%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF"]
QN_GL = ['Age','Result', 'GS', 'MP', 'FG', 'FGA', 'FG%', '3P', '3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']
REFORMAT =  ['Age','Result', 'GS', 'MP', 'FG', 'FGA', 'FG%','3P','3PA', '3P%', 'FT', 'FTA', 'FT%', 'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS', 'GmSc', '+/-']

def GraphAverages(d, players, stats = QN_AVG): 
    '''Graph players' career averages'''
    _graph_multiple_average(d, players, stats) if len (players) > 1 else _graph_single_averages(d, players, stats)
def GraphGamelogs(d, players, stats = QN_GL): 
    '''Graph players' gamelogs'''
    _graph_single_gamelogs(d, players, stats) if len (players) > 1 else _graph_multiple_gamelogs(d, players, stats)

GRAPH_FUNCTIONS = [GraphAverages, GraphGamelogs]

def _graph_multiple_average(d, players, stats) -> None:
    '''Graph 2+ players averages'''                  
    np = len(players)
    stat_list = _get_stat_averages(d, players, stats = stats.copy())
    fig, ax = plt.subplots(np, figsize=(15,3.5 * np))
    for set in stat_list:
        np -= 1
        player = set[0]
        vals = set[1:]
        ax[np].set_title(f"{player}'s stats:")
        b = ax[np].bar(x=stats, height=vals) ; ax[np].bar_label(b, vals)
def _graph_single_averages(d, player, stats) -> None:
    '''Graph 1 player's averages'''               
    stat_list = _get_stat_averages(d, [player], stats)
    plt.figure(figsize=(15,3.5)) ; plt.title(f"{player}'s stats:")
    b = plt.bar(x = stats, height = stat_list); plt.bar_label(b, stat_list)#if !to_list: (complete this if block if you want to_list to not also graph stats
def _graph_multiple_gamelogs(d, players, stats) -> None:
    '''Graph 2+ players' gamelogs'''                 
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
def _graph_single_gamelogs(d, player, stats) -> None:
    '''Graph 1 player's gamelogs'''
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

GRAPH_HELPERS = [_graph_multiple_average, _graph_single_averages, _graph_multiple_gamelogs, _graph_single_gamelogs]

def shrink_df(d, players, stats = QN_AVG) -> DataFrame:
    '''Shrink df to specified players, stats'''
    stats = stats.copy()
    if "Player" not in stats: stats.append("Player") 
    d = d[stats]
    return d[d['Player'].isin(players)]
def _get_stat_averages(d, players, stats) -> list:
    '''Returns [[list of players' stats]]'''
    stat_df = _shrink_df(d, players, stats = stats.copy())
    return_stats = []
    for player in players:
        player_df = stat_df[stat_df['Player'] == player]   
        player_stats = []
        for stat in stats:
            value = d[stat].iat[0]
            if "%" in stat: value *= 100
            if type(value) != str: value = round(value,2);player_stats.append(value)
        return_stats.append([player] + player_stats)
    return return_stats
def _clean_html(d, season_stats = False) -> DataFrame:
    '''Cleans player gamelogs, [optional] clean season_stats'''
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
        for stat in REFORMAT: d[stat] = d[stat].astype(float)
    return d
def _combine_dfs(player1, player2, career = False) -> DataFrame: 
    '''Returns a combined dataframe of 2 players' selected 'df' (gamelogs/career)'''
    return concat([player1.gamelogs, player2.gamelogs]) if career == False else concat([player1.career, player2.career])

STAT_HELPERS = [shrink_df, _get_stat_averages, _clean_html, _combine_dfs]