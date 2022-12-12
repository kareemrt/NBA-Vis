# Name: Kareem T
# Date: 12/11/2022
# Description: Unittest framework for NBA methods
import unittest
from methods import *
df = pd.read_csv('/Users/kareemtaha/Downloads/2022-2023 NBA Player Stats - Regular.csv', sep=";", index_col=0, encoding = 'latin') # the csv uses colons (;) instead of commas (,) to separate values
class Test_ParsePlayersDF(unittest.TestCase):

    def test_eval(self):
        print("Test 1: Test Evaluation | Function - GetPlayersDf\n================================================================\n")
        d = pd.concat([parse_player_df(df, ["Damian Lillard", "Stephen Curry", "Kevin Durant"], All_Stats), parse_player_df(df, ["LeBron James"], All_Stats), parse_player_df(df, ["Josh Hart", "Nassir Little"], All_Stats)])
        print(d)
        print("\n================================================================")


class Test_Visualize_Stats(unittest.TestCase):
    
    
    def test_multi_tolist(self):
        print("Test 2: Multiple ToList | Function - VisualizeStats\n================================================================\n")
        f = Visualize_Stats(df, players = ["Damian Lillard", "Stephen Curry"], to_list=True)
        print(f[1])
        print()
        print(f[0])
        print("\n================================================================")


    def test_single_tolist(self):
        print("Test 3: Single ToList | Function - VisualizeStats\n================================================================\n")
        d = Visualize_Stats(df, players = ["Josh Hart"], to_list=True)
        print(d)
        print("\n================================================================")

        
    def test_multi_stacked(self):
        print("Test 4: Multiple Stat-By-Stat | Function - VisualizeStats\n================================================================\n")
        d = Visualize_Stats(df, players = ["Damian Lillard", "Josh Hart"], stats=Quant_Stats, stacked_bar=True, to_list=True)
        for player_set in d:
            print(player_set[0] + 's stats')
            for i in range(len(Quant_Stats)-1):
                print(f'{Quant_Stats[i]}: {player_set[i+1]}')
        print("\n================================================================")


class Test_html(unittest.TestCase):

    def test_html(self):
        print("Test 5: Player Seasons HTML Test | Function - GetSeason\n================================================================\n")
        lebron_tag = "jamesle01"
        lebron_seasons = get_player_seasons_list(lebron_tag)
        print(lebron_seasons)
        print("\n================================================================")

    def test_gamelogs(self):
        print("Test 6: Player Gamelogs HTML Test | Function - GetGamelogsFromHTML\n================================================================\n")
        lebron_tag = "jamesle01"
        lebron_2022_games = get_player_gamelogs(lebron_tag, ['2010', '2020'])
        print(lebron_2022_games)
        print("\n================================================================")

    def test_clean(self):
        print("Test 7: Clean Player HTML DF | Function - CleanSeasonDF\n================================================================\n")
        lebron_tag = "jamesle01"
        lebron_seasons = get_player_seasons_list(lebron_tag)
        lebron_season4_games = get_player_gamelogs(lebron_tag, lebron_seasons[3])
        d = clean_gamelogs(lebron_season4_games)
        print(d)
        print("\n================================================================")

    def test_career_stats(self):
        print("Test 8: Player Career Stats HTML Test | Function - GetGamelogsFromHTML\n================================================================\n")
        lebron_tag = "jamesle01"
        lebron_career = get_player_career_stats(lebron_tag)
        print(lebron_career)
        print("\n================================================================")

if __name__ == "__main__":
    unittest.main()
