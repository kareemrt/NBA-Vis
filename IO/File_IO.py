import re # FILE I/O: Save (Franchise names/urls, Player names/url tags, League/Team/Player Objects) in Files to avoid saturating HTML requests
import shelve
import IO.HTML_IO as IO
def FileIO_Save_Franchise_Dict():
    '''Save Franchise Dict {Name: Url} to File (files/team_tags.txt)'''
    team_tags = IO.HTML_get_franchise_dict()
    with open("Data/franchise_dict.txt", "w") as teamfile:
        for team, tag in team_tags.items():
            teamfile.write(f"\n{team}: {tag}")
def FileIO_Save_Players_Dict(team_tags):
    '''Save Players Dict {Name: Url Tag} to File (files/league_tags.txt)'''
    league_tags = IO.HTML_get_player_dict( team_tags.values() )
    with open("Data/players_dict.txt", "w", encoding="utf-8") as leaguefile:
        for player, tag in league_tags.items(): leaguefile.write(f"\n{player}: {tag}") 
def FileIO_Load_Franchise_Dict():
    '''Read Franchise Dict {Name: Url} from File (files/team_tags.txt)'''
    team_tags = {}
    pattern = "(.*): (.*)"
    with open("Data/franchise_dict.txt", "r", encoding='utf-8') as teamfile:
        teamfile.readline()
        for line in teamfile.readlines(): 
            player, tag = re.findall(pattern, line)[0]
            team_tags[player] = tag
    return team_tags
def FileIO_Load_Players_Dict():
    '''Read Players Dict {Name: Url Tag} from File (files/league_tags.txt)'''
    league_tags = {}
    pattern = "(.*): (.*)"
    with open("Data/players_dict.txt", "r", encoding='utf-8') as leaguefile:
        leaguefile.readline()
        for line in leaguefile.readlines():
            player, tag = re.findall(pattern, line)[0]
            league_tags[player] = tag
    return league_tags
def FileIO_Save_Object(name, object):
    '''Save league/team/player objects to database file'''
    db = shelve.open("Data/League", writeback=True) # the writeback flag saves the object whenever it is closed, as opposed to only assignment
    db[name] = object
    db.close()
def FileIO_Load_Object(name):
    '''Load league/team/player objects from database file'''
    db = shelve.open("Data/League", writeback=True)
    object = db[name]
    db.close()
    return object
def FileIO_Load_HTML_Credentials():
    '''Load Socks5 username/password credentials for proxies'''
    with open("IO/Credentials.txt", "r") as c:
        username = c.readline().strip()
        password = c.readline().strip()
        credentials = c.readline().strip()
    return username, password, credentials
def FileIO_Load_HTML_Proxies():
    '''Load Socks5 proxies'''
    with open("IO/Proxies.txt") as p:
        proxies = p.readlines()
    return [proxy.strip() for proxy in proxies]
def FileIO_Load_HTML_Headers():
    '''Load html headers'''
    with open("IO/Headers.txt") as h:
        headers = h.readlines()
    return [header.strip() for header in headers]
