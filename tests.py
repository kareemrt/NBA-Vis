import unittest
from Functions import *
from Objects import *
from IO.HTML_IO import *
from IO.File_IO import FileIO_Object
from pandas import concat, read_csv
csv_df = read_csv('/Users/kareemtaha/Downloads/2022-2023 NBA Player Stats - Regular.csv', sep=";", index_col=0, encoding = 'latin') # the csv uses colons (;) instead of commas (,) to separate values

class Test_CSV_Functions(unittest.TestCase):

    def test_shrink_df(self):
        '''Intended: Shrink to players, stats'''
        print("\tTEST 1: Function - shrinkdf\n")
        print(concat([shrink_df(csv_df, ["Damian Lillard", "Stephen Curry", "Kevin Durant"], QN_AVG), shrink_df(csv_df, ["Josh Hart", "Nassir Little"], QN_AVG)]))

    def test_graph_averages_multiple(self):
        '''Intended: MatPlotLib stacked player averages'''
        print("\tTEST 2: Function - GraphAverages\n")
        GraphAverages(csv_df, ["Damian Lillard", "Stephen Curry"])

    def test_graph_averages_single(self):
        '''Intended: MatPlotLib stacked player averages'''
        print("\tTEST 3: Function - GraphAverages\n")
        GraphAverages(csv_df, ["Josh Hart"])
        
class Test_HTML_Functions(unittest.TestCase):
    def test_get_seasons(self):
        '''Intended: Print LeBron's career seasons'''
        print("\tTEST 4: Function - HTML_get_seasons\n")
        print(HTML_seasons("LeBron James"))

    def test_get_gamelogs(self):
        '''Intended: Print LeBron's gamelogs for 2010 & 2020'''
        print("\tTEST 5: Function - HTML_get_gamelogs\n")
        print(HTML_gamelogs(["LeBron James"], ['2010', '2020']))

    def test_get_averages(self):
        '''Intended: Print LeBron's career averages'''
        print("\tTEST 6: Function - HTML_get_career_stats\n")
        print(HTML_career_stats(["LeBron James"]))

class Test_Objects(unittest.TestCase):   
    def test_init(self):
        '''Intended: Create a Player object and print their representation'''
        print("\tTEST 7: Module - Objects.py\n")
        dame = Player("Damian Lillard")
        self.assertEqual(str(dame), "Player: Damian Lillard\nTag: lillada01\nSeasons Played: []\nTeams Played For: []")
        self.assertEqual(repr(dame), 'Player("Damian Lillard")')

    def test_stats(self):
        '''Intended: Print Dame's seasons, gamelogs, and career averages'''
        print("\tTEST 8: Module - Objects.py\n")

        Dame = Player("Damian Lillard")
        Dame.set_stats(gamelogs=True, career=True)
        print(Dame.seasons)
        print(Dame.gamelogs)
        print(Dame.career)

    def test_league(self):
        '''Intended: Create an NBA league with Blazer/Warrior teams having filled career averages; print dame/steph averages'''
        print("\tTEST 9: Module - Objects.py\n")
        NBA = League("NBA")
        NBA.create_teams()
        NBA.set_stats(gamelogs=False, career=True, teams=["Portland Trail Blazers", "Golden State Warriors"])
        players = NBA.get_players(["Damian Lillard", "Stephen Curry"])
        players.set_stats(setup = True, gamelogs = True)
        print(players["Damian Lillard"])
        print(players["Stephen Curry"])

class Test_FileIO(unittest.TestCase):
    def test_save_IO(self):
        '''Intended: Load an NBA league object and use it's methods to print season averages & dame's averages'''
        print("\tTEST 10: Module - File_IO.py\n")
        NBA = FileIO_Object("NBA2")
        Group = NBA.get_teams(["Portland Trail Blazers"]).set_stats(setup = True, career = True) # modify saved object
        print(Group.career)
        print(Group.gamelogs) 

if __name__ == "__main__":
    HTML_Suite = unittest.TestSuite()
    HTML_Suite.addTest(Test_HTML_Functions("test_get_seasons"))
    HTML_Suite.addTest(Test_HTML_Functions("test_get_gamelogs"))
    HTML_Suite.addTest(Test_HTML_Functions("test_get_averages"))
    Objects_Suite = unittest.TestSuite()
    #Objects_Suite.addTest(Test_Objects("test_init"))
    #Objects_Suite.addTest(Test_Objects("test_stats"))
    Objects_Suite.addTest(Test_Objects("test_league"))
    run = unittest.TextTestRunner()
    run.run(Objects_Suite)
    #run.run(HTML_Suite)

