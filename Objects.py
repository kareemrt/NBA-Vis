from pandas import DataFrame, concat, set_option # Object-Oriented implimentation for league/teams/players in the NBA vis program.
from IO.HTML_IO import HTML_get_player_dict, HTML_get_player_seasons, CLEAN_HTML_get_player_gamelogs, CLEAN_HTML_get_player_career_stats
from IO.File_IO import FileIO_Load_Franchise_Dict
from Functions import Visualize_Df

class League:

    def __init__(self, name) -> None:
        self.name = name
        self.teams = dict()
    def add_team(self, name, team) -> None: self.teams[name] = team
    def print_teams(self) -> None: 
        for team in self.teams.keys(): print(team)

    def set_teams(self) -> None:
        Franchise_Info = FileIO_Load_Franchise_Dict()
        Franchises = Franchise_Info.keys()
        for franchise in Franchises:
            url = Franchise_Info[franchise]
            team = Team(franchise, html = url)
            self.add_team(franchise, team)#; time.sleep(1)
        print(f"{self.name}'s teams have been set!")

    def set_players(self) -> None:
        for team in self.teams.values():
            team.set_players()#; time.sleep(1)
    def set_stats(self, teams = None, seasons = False, gamelogs = False, career = False, all_stats = False) -> None:
        if teams == None: teams = self.teams
        else:
            teams = dict() 
            for name in teams:
                team = self.teams.get(name)
                if team: teams[name] = team
        for name, team in teams.items(): 
            if seasons: team.set_player_seasons() ; print(f"Setting {name}'s player seasons!")
            if gamelogs: team.set_player_gamelogs() ; print(f"Setting {name}'s player gamelogs!")
            if career: team.set_player_career_stats() ; print(f"Setting {name}'s player career stats!")
            if seasons + gamelogs + career == 0: team.set_stats() ; print(f"Setting {name}'s seasons/gamelogs/career stats!")

    def get_teams(self, teams = None) -> dict: 
        if teams == None: teams = self.teams.keys()
        chosen = dict()
        for name in teams: 
            team = self.teams.get(name)
            if team: chosen[name] = team
        return chosen
    def get_players(self, players, teams = None) -> dict: 
        if teams == None: teams = self.teams.keys()
        chosen = dict()
        for franchise in teams:
            team = self.teams[franchise]
            for name in players:
                player = team.get_players([name])
                if player: chosen[name] = player[name]
        return chosen

class Team:

    def __init__(self, name, html = "") -> None:
        self.name = name
        self.roster_html = html
        self.players = {}
        self.gamelogs = []
        self.season_averages = []
    
    def add_player(self, name, player) -> None: self.players[name] = player
    def print_players(self) -> None:
        for name in self.players.keys(): print(name)
    def visualize(self):
        names = [player.name for player in self.players]
        Visualize_Df(self.season_averages, names)

    def set_players(self) -> None:
        team_players = HTML_get_player_dict([self.roster_html])
        for name, tag in team_players.items(): self.add_player(name, Player(name, tag = tag))
        print(f"{self.name}'s players have been created!")
    def set_player_seasons(self) -> None: 
        for player in self.players.values(): player.set_seasons() #;print(f"{self.name}'s players' seasons have been set!")
    def set_player_gamelogs(self, seasons) -> None:
        for player in self.players.values(): player.set_gamelogs(seasons) #;print(f"{self.name}'s players' gamelogs have been set!")
    def set_player_career_stats(self) -> None:
        for player in self.players.values(): player.set_career_stats() #;print(f"{self.name}'s players' career stats have been set!")
    def set_stats(self) -> None:
        for player in self.players.values(): player.set_stats()
    def set_season_averages(self):
        team_avg = DataFrame()
        set_option('mode.chained_assignment', None) # pandas option to avoid weird printing
        for player in self.players.values():
            avg = player.get_career_stats()
            if not avg.empty:
                szn_avg = avg[avg['Season'] == '2022-23']
                szn_avg['Player'] = player.name
                team_avg = concat([team_avg, szn_avg])
        self.season_averages = team_avg

    def get_players(self, players = None) -> dict:
        if players == None: players = self.players.keys()
        chosen = dict()
        for name in players:
            player = self.players.get(name)
            if player: chosen[name] = player
        return chosen
    def get_season_averages(self): return self.season_averages

class Player:

    def __init__(self, name, tag = "", seasons = [], teams = []):
        self.name = name
        self.tag = tag
        self.seasons = seasons
        self.teams = teams
        self.career_stats = None # stat : value
        self.gamelogs = DataFrame() # hash based over index approach for flexibility in case of future stat expansion, season : stat dict

    def visualize(self): Visualize_Df(self.career_stats, [self.name])

    def set_seasons(self) -> None: self.seasons = HTML_get_player_seasons(self.tag) #;print(f"{self.name}'s seasons have been set!")
    def set_gamelogs(self, seasons = None) -> None:
        if type(seasons) != "list": seasons = HTML_get_player_seasons(self.tag)
        self.gamelogs = CLEAN_HTML_get_player_gamelogs(self.tag, seasons)
    def set_career_stats(self) -> None: self.career_stats = CLEAN_HTML_get_player_career_stats(self.tag)
    def set_stats(self) -> None:
        '''Sets the seasons, career gamelogs, and season averages for a player'''
        self.set_seasons()
        self.set_gamelogs()
        self.set_career_stats()
        print(f"{self.name}'s stats have been set")

    def get_tag(self): return self.tag
    def get_seasons(self): return self.seasons
    def get_gamelogs(self) -> DataFrame: return self.gamelogs
    def get_career_stats(self) -> DataFrame: return self.career_stats


    def __str__(self) -> None:
        return f"Player: {self.name}\nSeasons Played: {self.seasons}\nTeams Played For: {self.teams}"
    def __repr__(self) -> str:
        return f"Player(\"{self.name}\")"