from pandas import DataFrame, concat, set_option # Object-Oriented implimentation for league/teams/players in the NBA vis program.
from IO.HTML_IO import HTML_player_tags, HTML_seasons, HTML_gamelogs, HTML_career_stats
from IO.File_IO import FileIO_Load_TeamsD, FileIO_Load_PlayersD
from Functions import GraphAverages, GraphGamelogs
from time import sleep

roster_htmls = FileIO_Load_TeamsD()
tags = FileIO_Load_PlayersD()
set_option('mode.chained_assignment', None)


class Group:
    '''Groups hold specified Player or Team objects'''
    def __init__(self, players = [], dict = None) -> None:
        self.members = {p:Player(p) for p in players} if dict == None else dict
        self.gamelogs = DataFrame()
        self.career = DataFrame()
    
    def __getitem__(self, item: str): return self.members[item]
    def values(self): return self.members.values()

    def set_stats(self, setup = False, gamelogs = False, career = False, seasons = None):
        for member in self.values():
            if setup: member.set_stats(gamelogs, career, seasons)
            if gamelogs and not member.gamelogs.empty: self.gamelogs = concat([self.gamelogs, member.gamelogs])
            if career and not member.career.empty: self.career = concat([self.career, member.career])

class League:
    '''League objects hold multiple Team objects'''
    def __init__(self, name) -> None:
        self.name = name
        self.teams = dict()
    def __str__(self): return f"League: {self.name}\nTeams: {list(self.teams.keys())}"
    def __repr__(self) -> str: return f"League('{self.name}')"
    
    def create_teams(self, stats = False, teams = roster_htmls.keys()) -> None:
        '''Populates League() with NEW Team() objects, optionally includes player stats''' 
        for t in teams: 
            self.teams[t] = Team(t)
            self.teams[t].create_players(stats)
            #OLOG.info(f"{self.name}: {t} created, stats_on = {stats}")
            sleep(1)

    def set_stats(self, gamelogs = False, career = False, seasons = None, teams = None) -> None:
        '''Sets stats (gamelogs/averages) for EXISTING Team() objects, optionally sets up player stats'''
        for team in self.get_teams(teams).values(): team.set_stats(gamelogs, career, seasons)
    
    def get_teams(self, teams = None) -> dict: 
        '''Returns Group {name, Team()} of a [list of teams]'''
        return Group(dict = dict(zip(teams, [self.teams[t] for t in teams]))) if teams != None else Group(dict = self.teams)
    
    def get_players(self, players, teams = None) -> dict:
        '''Returns Group {name, Player()} of a [list of players]'''
        if teams == None: teams = list(self.teams.keys()) # teams to search (all if user doesn't specify)
        assert type(players) == list and type(teams) == list
        chosen = dict()
        for franchise in teams: # search through teams
            team = self.teams[franchise] # get team object
            chosen = chosen | team.get_players(players).members
        return Group(dict = chosen)


class Team:
    def __init__(self, name) -> None:
        self.name = name
        self.html = roster_htmls[name]
        self.players = {}
        self.tags = HTML_player_tags([self.html])
        self.gamelogs = DataFrame()
        self.season_averages = DataFrame()
    def __str__(self) -> str: return f"Team: {self.name}\nPlayers: {list(self.players.keys())}"
    def __repr__(self) -> str: return f"Team('{self.name}')"
    
    def visualize(self, df_name, stats):
        '''Visualize a team's gamelogs OR career averages'''
        players = list(self.players.keys()) 
        if df_name[-1] == "s": df_name = df_name[:-1] # splice last char out
        match df_name.lower():
            case "gamelog": GraphGamelogs(self.gamelogs, players, stats)
            case "average": GraphAverages(self.season_averages, players, stats)
            case _: print("Pick a df: Gamelogs | Averages")

    def create_players(self, stats = False, players = None) -> None:
        '''Create NEW Player() objects, include stats if requested'''
        if players == None: players = list(self.tags.keys())
        for p in players: 
            self.players[p] = Player(p, [self.name])
            if stats: self.players[p].set_stats(True, True)
    
    def set_stats(self, gamelogs = False, career = False, seasons = None):
        '''Set Player() stats AND/OR Team() gamelogs/career_avgs for EXISTING Player() objects'''
        for p in self.players.values():
            if not gamelogs and not career: p.set_stats(); continue# If no stats selected then setup the player stats
            
            logs, avgs = p.gamelogs, p.career # GET PLAYER STATS
            logs['Player'] = p.name ; avgs['Player'] = p.name # Mark that player
            if gamelogs and not logs.empty: self.gamelogs = concat([self.gamelogs, logs]) # add to team
            if career and not avgs.empty: self.season_averages = concat([self.season_averages, avgs])
   
    def get_players(self, players = None) -> dict: 
        '''Returns a dict {name: player()} given a [list of player names]'''
        if players == None: return Group(dict = self.players)
        on = [p for p in players if p in self.players.keys()] # find players ON team
        return Group(dict = dict(zip(on, [self.players[p] for p in on])))

class Player:
    def __init__(self, name, teams = [], seasons = []):
        self.name   , self.tag = name, tags[name]
        self.seasons, self.teams = seasons, teams
        self.career , self.gamelogs = DataFrame(), DataFrame()
    def __str__(self) -> None: return f"Player: {self.name}\nTag: {self.tag}\nSeasons Played: {self.seasons}\nTeams Played For: {self.teams}"
    def __repr__(self) -> str: return f"Player(\"{self.name}\")"

    def visualize(self, df_name, stats):
        '''Visualize a player's gamelogs/career averages with specified stats''' 
        if df_name[-1] == "s": df_name = df_name[:-1] # string cleaning to find which df user wants (splice last char)
        match df_name.lower():
            case "gamelog": GraphGamelogs(self.gamelogs, [self.name], stats)
            case "average": GraphAverages(self.career, [self.name], stats)
            case _: print("Pick a df: Gamelogs | Averages")
    
    def set_stats(self, gamelogs = False, career = False, seasons = None) -> None:
        '''Sets a player's seasons / career gamelogs / career averages'''
        sleep(1.5)
        try:
            if seasons == None: self.seasons = HTML_seasons(self.name)
            if not gamelogs and not career: self.gamelogs, self.career = HTML_gamelogs(self.name, self.seasons), HTML_career_stats(self.name)
            if gamelogs: 
                if type(seasons) != "list": seasons = self.seasons
                self.gamelogs = HTML_gamelogs(self.name, seasons)
            if career: self.career = HTML_career_stats(self.name)
        except Exception as e: print(e); pass


