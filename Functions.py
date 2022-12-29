from pandas import DataFrame
import matplotlib.pyplot as plt

Qual_Stats = ["Pos", "Tm"]
Quant_Stats_CSV = ["Age", "G", "GS", "MP", "PTS", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P","2PA","2P%","eFG%","FT","FTA","FT%","ORB","DRB","TRB","AST","STL","BLK","TOV","PF"]
All_Stats = Qual_Stats + Quant_Stats_CSV


def Visualize_Df(d, players, stats = Quant_Stats_CSV, to_list = False, stacked_bar = False):
    '''Graph the selected players stats as a dataframe, returns a list of those stats if specified. \nOutput: matplotlib graph AND/OR list(str/int)   
    * d- df: data.
    * players- list(str): player(s).
    * stats- list (str): stats from d to visualize.
    * to_list- bool: returns a list of the visualized stats. If multiple players, returns a 2D list.
    note: if 2D, each list indexes (e.g. Visualize_Stats()[0] vs Visualize_Stats[1]) players and sub-indexes (Vis_S[0][0] vs Vis_S[0][1]) are different stats for that player. '''
    try: assert len(stats) > 0 
    except AssertionError: stats = ["PTS"] # Make sure there are stats to visualize
    stats = stats.copy()
    d = d[["Player"] + stats]                  # .. - shrink to stats (retain player to search their stats later)                          
    stat_df = shrink_df(d, players, stats = stats)

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
    
    if len(selected) > 0: Visualize_Df(d, selected, stacked_bar = stacked_bar)
    else: print("No players given!")

Display_Functions = [Visualize_Df, Live_Compare]

def get_tags_from_dict(tag_dict, players): 
    '''Produce a list of player tags given a list of players
    * league_tags- dict(str:str): dict {players:tags} in the NBA
    * players- list(str): list of players to produce tags of}'''
    return [tag_dict.get(player) for player in players]
def shrink_df(d, players, stats = Quant_Stats_CSV) -> DataFrame:
    '''Shrink df to specified players, stats
    * d- df: data\nplayers- list(str): player(s)
    * stats- list(str): stats from d to visualize'''
    if stats != None: #User specifies certain stats (non-default)
        stats = stats.copy()
        try: assert "Player" in stats #Makes sure that when we shrink the df to those stats, we don't accidentally remove the Player Name col (needed for compares)
        except AssertionError: stats.append("Player") 
        d = d[stats]
    d = d[d['Player'].isin(players)]
    return d
def clean_gamelogs(d, season_stats = False) -> DataFrame:
    '''Produce a cleaned DataFrame of a player's gamelogs/season_stats given a dirty DataFrame
    * d- df: data'''
    d = d.copy() # Copy the original df to avoid errors
    d.dropna(subset=['Age'], inplace=True)
    d = d[d['Age'] != 'Age'] # = d[d["Rk"] != "Rk"] # Remove extra rows (there are rows that repeat the original column headers, but do not contain values (because the table is 80+ rows))
    if not season_stats: 
        d.rename(columns = {'Rk':'Game', 'G':'Played','Unnamed: 5':'Away', 'Unnamed: 7': 'Result'}, inplace = True) # rename column headers
        d.set_index('Game', inplace = True) # Set the game # as the index
        d['Away'].mask(d['Away'] == '@', True, inplace=True);d['Away'] = d['Away'].fillna(False) # replace values in away column with bool
        d.dropna(subset=['Played'], inplace=True) # drop unplayed games
    return d
def clean_career_stats(d) -> DataFrame:
    '''Description: Produce a cleaned DataFrame of a player's gamelogs/season_stats given a dirty DataFrame
    * d- df: data'''
    return clean_gamelogs(d, season_stats = True)

Clean_Functions = [get_tags_from_dict, shrink_df, clean_gamelogs, clean_career_stats]
