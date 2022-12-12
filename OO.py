# Name: Kareem T (github/kareemrt)
# Date: 12/11/2022
# Description: Object-Oriented Implimentation of the stats-base for the NBA Visualizer program.
class League:

    def __init__(self) -> None:
        self.name = ""
        self.teams = []
class Team:

    def __init__(self) -> None:
        self.name = ""
        self.players = []

class Player:

    def __init__(self) -> None:
        self.name = ""
        self.career_stats = {}
        self.season_stats = {}