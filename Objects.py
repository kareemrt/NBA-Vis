from pandas import DataFrame # Object-Oriented implimentation for league/teams/players in the NBA vis program.
from IO.HTML_IO import HTML_get_player_dict, HTML_get_player_seasons, CLEAN_HTML_get_player_gamelogs, CLEAN_HTML_get_player_career_stats
from IO.File_IO import FileIO_Load_Franchise_Dict
import time

class League:

    def __init__(self, name) -> None:
        self.name = name
        self.teams = []

    def set_teams(self) -> None:
        Franchise_Info = FileIO_Load_Franchise_Dict()
        Franchises = Franchise_Info.keys()
        for franchise in Franchises:
            url = Franchise_Info[franchise]
            team = Team(franchise, html = url)
            self.add_team(team); time.sleep(.5)

    def add_team(self, Team) -> None:
        self.teams.append(Team)

    def print_teams(self) -> None:
        for team in self.teams: print(team.name)
    def get_team(self, Team): 
        for team in self.teams: 
            if team.name == Team: return team
    

class Team:

    def __init__(self, name, html = "") -> None:
        self.name = name
        self.html = html
        self.players = []
        self.gamelogs = []

    def set_players(self) -> None:
        self.players = []
        team_players = HTML_get_player_dict([self.html])
        for name, tag in team_players.items():
            player = Player(name, tag = tag)
            self.add_player(player)
    def set_player_seasons(self) -> None: 
        for player in self.players: player.set_seasons() ; time.sleep(0.5)
    def set_player_gamelogs(self, seasons) -> None:
        for player in self.players: player.set_gamelogs(seasons) ; time.sleep(0.5)
    def set_player_career_stats(self) -> None:
        for player in self.players: player.set_career_stats() ; time.sleep(0.5)

    def add_player(self, Player) -> None: self.players.append(Player)
    

    def print_players(self) -> None:
        for player in self.players: print(player.name)
    def get_players(self) -> list:
        return self.players

class Player:

    def __init__(self, name, tag = "", seasons = [], teams = []) -> None:
        self.name = name
        self.tag = tag
        self.seasons = seasons
        self.teams = teams
        self.career_stats = None # stat : value
        self.gamelogs = DataFrame() # hash based over index approach for flexibility in case of future stat expansion, season : stat dict

    def set_tag(self, tag) -> None: self.tag = tag
    def set_seasons(self) -> None:
        tag = self.get_tag()
        seasons = HTML_get_player_seasons(tag)
        self.seasons = seasons
    def set_gamelogs(self, seasons) -> None:
        tag = self.get_tag()
        gamelogs = CLEAN_HTML_get_player_gamelogs(tag, seasons)
        self.gamelogs = gamelogs
    def set_career_stats(self) -> None:
        tag = self.get_tag()
        career_stats = CLEAN_HTML_get_player_career_stats(tag)
        self.career_stats = career_stats

    def get_tag(self): return self.tag
    def get_seasons(self): return self.seasons
    def get_gamelogs(self) -> DataFrame: return self.gamelogs
    def get_career_stats(self) -> DataFrame: return self.career_stats


    def __str__(self) -> None:
        return f"Player: {self.name}\nSeasons Played: {self.seasons}\nTeams Played For: {self.teams}"
    def __repr__(self) -> str:
        return f"Player(\"{self.name}\")"