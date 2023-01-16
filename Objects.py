from pandas import DataFrame, concat, set_option # Object-Oriented implimentation for league/teams/players in the NBA vis program.
from IO.HTML_IO import HTML_get_player_dict, HTML_get_player_seasons, CLEAN_HTML_get_player_gamelogs, CLEAN_HTML_get_player_career_stats
from IO.File_IO import FileIO_Load_Franchise_Dict, FileIO_Load_Players_Dict
from Functions import Graph_Averages_DF, Graph_Gamelog_Df, Visualize_Spec_df
from time import sleep
roster_htmls = FileIO_Load_Franchise_Dict()
tags = FileIO_Load_Players_Dict()
class League:
    def __init__(self, name) -> None:
        self.name = name
        self.teams = dict()
    
    def add_team(self, name, team) -> None: self.teams[name] = team
    def print_teams(self) -> None: 
        for team in self.teams.keys(): print(team)

    def set_teams(self) -> None:
        Franchises = roster_htmls.keys()
        for franchise in Franchises:
            team = Team(franchise)
            team.set_url()
            team.set_players()
            self.add_team(franchise, team)
    def set_stats(self, seasons = None, teams = None, gamelogs = False, career = False) -> None:
        if teams == None: t = self.teams
        else:
            t = dict()
            for name in teams:
                team = self.teams.get(name)
                if team: t[name] = team
        for name, team in t.items():
            if seasons: team.set_seasons() 
            if gamelogs: team.set_gamelogs() ; print(f"Setting {name}'s player gamelogs!")
            if career: team.set_career_stats() ; print(f"Setting {name}'s player career stats!")
            if gamelogs + career == 0: team.set_stats() ; print(f"Setting {name}'s seasons/gamelogs/career stats!")
            sleep(1)
    
    def get_teams(self, teams = None) -> dict: 
        if teams == None: return self.teams
        assert type(teams) == list
        chosen = dict()
        for name in teams: # of teams user wants
            team = self.teams.get(name) # try to get from league
            if team: chosen[name] = team # if exist add to return dict
        return chosen
    def get_players(self, players, teams = None) -> dict:
        if teams == None: teams = list(self.teams.keys()) # teams to search (all if user doesn't specify)
        assert type(players) == list and type(teams) == list
        chosen = dict()
        for franchise in teams: # search through teams
            team = self.teams[franchise] # (by getting team from league)
            for name in players:         # search desired players
                player = team.get_players([name])       # in team
                if player: chosen[name] = player[name]  # if exist add to return dict
        return chosen

class Team:
    def __init__(self, name) -> None:
        self.name = name
        self.roster_html = roster_htmls[name]
        self.players = {}
        self.gamelogs = DataFrame()
        self.season_averages = DataFrame()
    
    def print_players(self) -> None:
        for name in self.players.keys(): print(name)
    def visualize(self, df_name, stats):
        players = list(self.players.keys()) 
        if df_name[-1] == "s": df_name = df_name[:-1] # splice last char out
        match df_name.lower():
            case "gamelog": Graph_Gamelog_Df(self.gamelogs, players, stats)
            case "average": Graph_Averages_DF(self.season_averages, players, stats)
            case _: print("Pick a df: Gamelogs | Averages")

    def set_players(self) -> None:
        team_players = HTML_get_player_dict([self.roster_html])
        for player in team_players.keys(): self.players[player] = Player(name = player, teams = [self.name])
        print(f"{self.name}'s players have been created!")
    def set_stats(self, seasons = False, gamelogs = False, career = False) -> None:
        for player in self.players.values(): 
            if seasons: player.set_seasons()
            if gamelogs: player.set_gamelogs()
            if career: player.set_career_stats()
            if not seasons and not gamelogs and not career: player.set_stats()
    def set_gamelogs(self):
        set_option('mode.chained_assignment', None) # pandas option to avoid weird printing
        team_gamelogs = DataFrame()
        for player in self.players.values():
            gamelogs = player.get_gamelogs()
            gamelogs['Player']  = player.name
            if not gamelogs.empty: team_gamelogs = concat([team_gamelogs, gamelogs])
        self.gamelogs = team_gamelogs
    def set_season_averages(self):
        team_avg = DataFrame()
        set_option('mode.chained_assignment', None) # pandas option to avoid weird printing
        for player in self.players.values():
            avg = player.get_career_stats()
            avg['Player']  = player.name
            if not avg.empty: team_avg = concat([team_avg, avg])
        self.season_averages = team_avg

    def get_players(self, players = None) -> dict:
        if players == None: return self.players
        chosen = dict()
        for name in players:
            player = self.players.get(name)
            if player: chosen[name] = player
        return chosen
class Player:
    def __init__(self, name, seasons = [], teams = []):
        self.name = name
        self.tag = tags[name]
        self.seasons = seasons
        self.teams = teams
        self.valid = False
        self.career_stats = DataFrame() # stat : value
        self.gamelogs = DataFrame() # hash based over index approach for flexibility in case of future stat expansion, season : stat dict

    def visualize(self, df_name, stats): 
        assert self.valid # we don't want to visualize players without complete stats (a tag, gamelogs, and averages)
        if df_name[-1] == "s": df_name = df_name[:-1] # string cleaning to find which df user wants (splice last char)
        match df_name.lower():
            case "gamelog": Graph_Gamelog_Df(d = self.gamelogs, players = [self.name], stats=stats)
            case "average": Graph_Averages_DF(d = self.career_stats, players = [self.name], stats=stats)
            case _: print("Pick a df: Gamelogs | Averages")
    def check_validity(self): self.valid = self.career_stats.empty == False and self.gamelogs.empty == False and len(self.seasons) > 0
    
    def set_seasons(self) -> None: self.seasons = HTML_get_player_seasons(self.tag)
    def set_gamelogs(self, seasons = None) -> None:
        if type(seasons) != "list": seasons = self.seasons
        self.gamelogs = CLEAN_HTML_get_player_gamelogs(self.tag, seasons)
    def set_career_stats(self) -> None: self.career_stats = CLEAN_HTML_get_player_career_stats(self.tag)
    def set_stats(self, seasons = None) -> None:
        '''Sets the seasons, career gamelogs, and season averages for a player'''
        try:
            self.set_seasons()
            self.set_gamelogs(seasons=seasons)
            self.set_career_stats()
            self.check_validity()
            print(f"{self.name}'s stats have been set")
        except KeyError as e: print(e); pass

    def __str__(self) -> None: return f"Player: {self.name}\nSeasons Played: {self.seasons}\nTeams Played For: {self.teams}"
    def __repr__(self) -> str: return f"Player(\"{self.name}\")"

class Group:
    def __init__(self, players) -> None:
        players = {player:Player(player) for player in players}
        teams = []
        seasons = DataFrame()
        career_stats = DataFrame()
