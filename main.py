# Name : Msin.py
# Auth : KT
# Desc : User Module
import IO.WebScraper as WS
import IO.DB as DB

def populate_DB(players = False, gamelogs = False, career = False, teams = False):
    '''Populate different SQLite tables'''
    teams = WS.Get_Teams()
    roster = WS.Get_Players(teams)
    for i, (player, (tag, team)) in enumerate(roster.items()):
        if players: DB.save_players(player, tag, team)
        elif gamelogs: 
            seasons = WS.Get_Seasons(tag)
            playerlogs = WS.Get_Gamelogs(player, tag, seasons)
            DB.save_gamelogs(playerlogs.values)
        elif career: 
            career_stats = WS.Get_Career(player, tag)
            DB.save_career(career_stats.values)
        print(f"{i}: {player}'s stats have been set".encode('utf-8'))
        WS.time.sleep(1)
    if teams: DB.save_teams(teams)

def query(query): 
    '''SQL query''' 
    return DB.query(query)


def main():
    # THESE 3 NEED PROXY INSTALL
    # populate_DB(players=True, teams=True)
    # populate_DB(gamelogs=True)
    # populate_DB(career=True)
    # THESE 4 WORK OUT OF BOX ( NO PROXY )
    query('SELECT * FROM Players')
    # query('SELECT * FROM Teams')
    # query('SELECT * FROM Gamelogs')
    # query('SELECT * FROM Career')


if __name__ == "__main__":
    main()
