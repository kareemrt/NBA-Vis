import re               # FILE I/O: Save (Franchise names/urls, Player names/url tags, League/Team/Player Objects) in Files to avoid saturating HTML requests
import shelve
import IO.HTML_IO as IO

def FileIO_Save_TeamsD():
    '''Save Franchise Dict {Name: Url} to File (files/team_tags.txt)'''
    tags = IO.HTML_team_urls()
    with open("Data/franchise_dict.txt", "w") as f:
        for team, tag in tags.items():
            f.write(f"\n{team}: {tag}")

def FileIO_Save_PlayersD():
    '''Save Players Dict {Name: Url Tag} to File (files/league_tags.txt)'''
    tags = IO.HTML_player_tags(roster_htmls = FileIO_Load_TeamsD().values())
    with open("Data/players_dict.txt", "w", encoding="utf-8") as f:
        for player, tag in tags.items(): f.write(f"\n{player}: {tag}")

def FileIO_Load_TeamsD():
    '''Read Franchise Dict {Name: Url} from File (files/team_tags.txt)'''
    tags = {}
    pattern = "(.*): (.*)"
    with open("Data/franchise_dict.txt", "r", encoding='utf-8') as f:
        f.readline()
        for line in f.readlines(): 
            player, tag = re.findall(pattern, line)[0]
            tags[player] = tag
    return tags

def FileIO_Load_PlayersD():
    '''Read Players Dict {Name: Url Tag} from File (files/league_tags.txt)'''
    tags = {}
    pattern = "(.*): (.*)"
    with open("Data/players_dict.txt", "r", encoding='utf-8') as f:
        f.readline()
        for line in f.readlines():
            player, tag = re.findall(pattern, line)[0]
            tags[player] = tag
    return tags

def FileIO_Object(object, save = False):
    '''Load/Save objects (League/Team/Player) to file'''
    with shelve.open("Data/League", writeback=True) as db: # the writeback flag saves the object whenever it is closed, as opposed to only assignment
        if save: db[object.name] = object
        else: return db[object]

def FileIO_HTML():
    '''Loads HTML headers, alongside Socks5 proxies, including proxy username, password, and credentials'''
    with open("IO/Credentials.txt", "r") as c:
        username = c.readline().strip()
        password = c.readline().strip()
        credentials = c.readline().strip()
    with open("IO/Proxies.txt") as p: proxies = [proxy.strip() for proxy in p.readlines()]
    with open("IO/Headers.txt") as h: headers = [header.strip() for header in h.readlines()]
    return username, password, credentials, proxies, headers