# Name : Main.py
# Auth : Kareem T
# Date : 1/29/24
# Desc : User Module, Backend program for DB population/query
import IO.WebScraper as WS
import IO.DB as DB
import multiprocessing as mp
import time
import os

lock = mp.Lock()

def populate_DB(ps, glogs, car, plogs, poffs, franch, year_queue = None):
    '''Populate MySQL tables
    ps - Players             |glogs - Gamelogs      |car - Career
    plogs - Playoff Gamelogs |poffs - Playoff Teams |franch - NBA Teams'''
    process_name = mp.current_process().name
    if car:
        all_players = DB.query('SELECT Player, Tag FROM Players P')
        players_in_career = DB.query('SELECT min(Player) as x, Tag t FROM Career C GROUP BY C.t')
        seen_players = {}
        all_stats = WS.pd.DataFrame()
        for i, (player, tag) in enumerate(all_players):
            if seen_players.get(tag, None) != None: continue # Player already in Career table
            seen_players[tag] = player
            all_stats = WS.pd.concat([all_stats, WS.Get_Career(player, tag)])
            if i % 10 == 0: DB.save_career(all_stats) # Save to DB every 10 players (helps handle web-scraper exceptions)
        DB.save_career(all_stats)
    # Tables: ( Players, Gamelogs (Non-playoffs), Career, Teams, Playoffs, Gamelogs (Playoffs) )
    for y in iter(year_queue.get, None): # Get year from multi-processing queue
        print(f'Processing {y}')
        teams = WS.Get_Teams(y)
        while len(teams) == 0: 
            print(teams)
            teams = WS.Get_Teams(y)
        # Check if Table needs player roster (Players, gamelogs)
        if ps or glogs: 
            for teamtag, team in teams:
                
                # Get roster given team, year
                roster = WS.Get_Players(teamtag, y)
                for i, (player, tag) in enumerate(roster.items()):

                    # Table: Players
                    if ps: DB.save_player(player, tag, team, teamtag, y)

                    # Table: Gamelogs (non-playoff games)
                    elif glogs:
                        playerlogs = WS.Get_Gamelogs(player, tag, y)
                        DB.save_gamelogs(playerlogs.values)

                    # Table: Career (stats)
                    elif car:
                        
                        career_stats = WS.Get_Career(player, tag) # this method does not discriminate if player already exists
                        DB.save_career(career_stats.values)  
            
                    print(f"{i}: {player}'s {y} stats have been set by {process_name}".encode('utf-8'))
                    #time.sleep(0.5)

        # Table: Teams
        if franch: DB.save_teams(y, teams)

        # Table: Playoffs
        if poffs:
            qualified = WS.Get_Playoffs(y)
            DB.save_playoffs(y,  qualified)

        # Table: Gamelogs (Playoffs)
        if plogs:
            # retrieve (player, tag, [seasons]) for all playoff players
            qualified = DB.query(f'SELECT C.Player, C.Season, B.Tag FROM Career C JOIN Players B on C.Player == B.Player JOIN Teams t on C.Team==t.Abbrev JOIN Playoffs z ON (z.Team==t.Team AND C.Season==z.Season)')
            for player, season, tag in qualified:
                print(player, season, tag)
                playerlogs = WS.Get_Gamelogs(player, tag, season, playoffs=True)
                DB.save_gamelogs(playerlogs.values)
                    
            time.sleep(0.5)

def multi_process(players = False, glogs = False, career = False, plogs = False, poffs = False, franch = False, years = None, proxy = True):
    '''Create multiple processes to concurrently handle WebScraping IO'''

    if proxy: os.environ['USE_PROXY'] = "1"
    # Get teams for specified seasons
    if not years: years = list(range(1968, 2025))

    # Create multi-processing queue, place years into it
    year_queue = mp.Queue()
    for y in years: year_queue.put(y)
    for _ in range(2): year_queue.put(None) # Kill signal to stop processes

    # Create multi-processes
    p1 = mp.Process(target = populate_DB, name="Worker 1", args=(players, glogs, career, plogs, poffs, franch, year_queue))
    p2 = mp.Process(target = populate_DB, name="Worker 2", args=(players, glogs, career, plogs, poffs, franch, year_queue))
    p3 = mp.Process(target = populate_DB, name="Worker 3", args=(players, glogs, career, plogs, poffs, franch, year_queue))
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

def query(query): 
    '''SQL query''' 
    return DB.query(query)


def user_query():
    '''User function for querying data'''
    # sample queries:
    #stats = query('SELECT * FROM Gamelogs WHERE Date == "2023-01-06" AND (Team == "POR" OR Team == "IND")')
    #stats = query('SELECT C.Player, C.Season, B.Tag FROM Career C JOIN Players B on C.Player == B.Player JOIN Teams t on C.Team==t.Abbrev JOIN Playoffs z ON (z.Team==t.Team AND C.Season==z.Season)')
    #for stat in stats:print(stat)
    # query('SELECT * FROM Teams')
    while(True):
        q = input("Input SQL Query")
        for stat in query(q): print(stat)
        if input("Still playing?").lower() != "yes": break


if __name__ == "__main__":
    #multi_process(players=True, years=range(1982,2022), proxy=True)
    user_query()