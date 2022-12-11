import unittest
from methods import *


df = pd.read_csv('/Users/Kareem/Downloads/2022-2023 NBA Player Stats - Regular.csv', sep=";", index_col=0, encoding = 'latin') # the csv uses colons (;) instead of commas (,) to separate values

class TestGetPlayersDF(unittest.TestCase):

    def test_eval(self):
        print("Test 1: Test Evaluation | Function - GetPlayersDf\n================================================================n")
        d = pd.concat([Get_Players_df(df, ["Damian Lillard", "Stephen Curry", "Kevin Durant"], All_Stats), Get_Players_df(df, ["LeBron James"], All_Stats), Get_Players_df(df, ["Josh Hart", "Nassir Little"], All_Stats)])
        print(d)

class Test_Visualize_Stats(unittest.TestCase):
    
    
    def test_multi_tolist(self):
        print("Test 2: Multiple ToList | Function - VisualizeStats\n================================================================n")

        f = Visualize_Stats(df, players = ["Damian Lillard", "Stephen Curry"], to_list=True)
        print(f[1])
        print()
        print(f[0])

    def test_single_tolist(self):
        print("Test 3: Single ToList | Function - VisualizeStats\n================================================================n")
        d = Visualize_Stats(df, players = ["Josh Hart"], to_list=True)
        print(d)
        
    def test_multi_stacked(self):
        print("Test 4: Multiple Stat-By-Stat | Function - VisualizeStats\n================================================================\n")
        d = Visualize_Stats(df, players = ["Damian Lillard", "Josh Hart"], stats=Quant_Stats, stacked_bar=True, to_list=True)
        for player_set in d:
            print(player_set[0] + 's stats')
            for i in range(len(Quant_Stats)-1):
                print(f'{Quant_Stats[i]}: {player_set[i+1]}')

class Test_html(unittest.TestCase):

    def test_html(self):
        print("Test 5: Player Seasons HTML Test | Function - GetSeason\n================================================================\n")
        lebron_seasons = get_seasons("https://www.basketball-reference.com/players/j/jamesle01.html#per_game")
        print(lebron_seasons)
    
    def test_gamelogs(self):
        print("Test 6: Player Gamelogs HTML Test | Function - GetGamelogsFromHTML\n================================================================n")
        lebron_seasons = get_seasons("https://www.basketball-reference.com/players/j/jamesle01.html#per_game")
        lebron_tag = "jamesle01"
        d = get_gamelog_from_player_html(lebron_tag, lebron_seasons[3])
        print(d)
    def test_clean(self):
        print("Test 7: Clean Player HTML DF | Function - CleanSeasonDF\n================================================================n")
        lebron_seasons = get_seasons("https://www.basketball-reference.com/players/j/jamesle01.html#per_game")
        lebron_tag = "jamesle01"
        lebron_season4 = get_gamelog_from_player_html(lebron_tag, lebron_seasons[3])
        d = clean_season_df(lebron_season4)
        print(d)

if __name__ == "__main__":
    unittest.main()
