import re # FILE I/O: Save (Franchise names/urls, Player names/url tags, League/Team/Player Objects) in Files to avoid saturating HTML requests
import shelve
from IO.HTML_IO import HTML_get_franchise_dict, HTML_get_player_dict

def FileIO_Save_Franchise_Dict():
#   Save Franchise Dict {Name: Url} to File (files/team_tags.txt)
    team_tags = HTML_get_franchise_dict()
    with open("Data/franchise_dict.txt", "w") as teamfile:
        for team, tag in team_tags.items():
            teamfile.write(f"\n{team}: {tag}")

def FileIO_Save_Players_Dict(team_tags):
#   Save Players Dict {Name: Url Tag} to File (files/league_tags.txt)
    league_tags = HTML_get_player_dict( team_tags.values() )
    with open("Data/players_dict.txt", "w") as leaguefile:
        for player, tag in league_tags.items(): leaguefile.write(f"\n{player}: {tag}") 

def FileIO_Load_Franchise_Dict():
#   Read Franchise Dict {Name: Url} from File (files/team_tags.txt)
    team_tags = {}
    pattern = "(.*): (.*)"
    with open("Data/franchise_dict.txt", "r") as teamfile:
        teamfile.readline()
        for line in teamfile.readlines(): 
            player, tag = re.findall(pattern, line)[0]
            team_tags[player] = tag
    return team_tags

def FileIO_Load_Players_Dict():
#   Read Players Dict {Name: Url Tag} from File (files/league_tags.txt)
    league_tags = {}
    pattern = "(.*): (.*)"
    with open("Data/players_dict.txt", "r") as leaguefile:
        leaguefile.readline()
        for line in leaguefile.readlines():
            player, tag = re.findall(pattern, line)[0]
            league_tags[player] = tag
    return league_tags

def FileIO_Save_Object(name, object):
    db = shelve.open("Data/League")
    db[name] = object
    db.close()

def FileIO_Load_Object(name):
    db = shelve.open("Data/League")
    object = db[name]
    db.close()
    return object
