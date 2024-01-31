# Name : DB.py
# Auth : KT
# Desc : Module that interacts with MySQL database
import mysql.connector as sql
import logging
import multiprocessing as mp
import os

host = os.environ['UNIX_SOCKET']
user = os.environ['USER']
password = os.environ['PASS']
database = os.environ['DB']

logger = logging.getLogger()
file_handler = logging.FileHandler('src/Logs/net.log', encoding='utf-8', mode='a'); file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')); file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

lock = mp.Lock()

def query(query):
    '''SQL query'''
    with lock:
        try: 
            conn = sql.connect(unix_socket=host, user=user, password=password, database=database)
            if conn.is_connected():
                print(f"Connected to MySQL server: {host}")
                c = conn.cursor()
                c.execute(query)
                rows = c.fetchall()
                conn.commit()
                return rows

        except Exception as err: print(f"Error: {err}")
        finally: # Close the connection when done
            if 'connection' in locals():
                conn.close()
                print("Connection closed")

def save_player(player, tag, team, teamtag, season):
    '''Populate the players table'''
    with lock:
        # Connect
        try: 
            conn = sql.connect(host=host, user=user, password=password, database=database)
            if conn.is_connected():
                c = conn.cursor()

                # Insert, but check to prevent duplicate record insertion
                c.execute('SELECT COUNT(*) FROM Players WHERE Player = %s AND Tag = %s AND Team = %s', (player, tag, team)) # Insert
                if c.fetchone()[0] <= 0: 
                    c.execute("INSERT INTO Players (Player, Tag, Team, TTag, Start, End) VALUES (%s, %s, %s, %s, %s, %s)", (player, tag, team, teamtag, season, season))
                    conn.commit()
                    return
                
                # Update 'start' season (no insert)
                c.execute("SELECT COUNT(*) FROM Players WHERE Player = %s AND Tag = %s AND Team = %s AND Start > %s", (player, tag, team, season))
                if c.fetchone()[0] > 0:
                    c.execute('UPDATE Players SET Start = %s WHERE Player = %s AND Tag = %s AND Team = %s', (season, player, tag, team))
                
                # Update 'end' season (no insert)
                c.execute("SELECT COUNT(*) FROM Players WHERE Player = %s AND Tag = %s AND Team = %s AND End < %s", (player, tag, team, season))
                if c.fetchone()[0] > 0:
                    c.execute('UPDATE Players SET End = %s WHERE Player = %s AND Tag = %s AND Team = %s', (season, player, tag, team))
                conn.commit()
                
        except Exception as err: print(f"Error: {err}")
        finally: # Close the connection when done
            if 'connection' in locals():
                conn.close()
                print("Connection closed")    

def save_gamelogs(gamelogs):
    '''Save a np matrix of gamelogs into the SQLite DB, log-by-log'''
    with lock:
        try:
            conn = sql.connect(host=host, user=user, password=password, database=database)
            c = conn.cursor()
            # Iterate log by log
            for date, age, team, away, opp, res, gs, mp, fg, fga, fgp, tp, tpa, tpp, ft, fta, ftp, orb, drb, reb, ast, stl, blk, tov, pf, pts, gmsc, pm, season, player, playoff in gamelogs:
                # Convert formats where necessary and put in correct order
                data = (player, season, pts, date, team, opp, int(away), res, int(res>0), round(mp,2), gs, round(age,3), playoff, fg, fga, round(fgp*100,3), tp, tpa, round(tpp*100,3), ft, fta, round(ftp*100,3), orb, drb, reb, ast, stl, blk, tov, pf, gmsc, pm)
                # Use query to prevent inserting duplicates (by making sure there is no count of that log)
                c.execute('SELECT COUNT(*) FROM Gamelogs WHERE Player = %s AND Date = %s', (player, date))
                if c.fetchone()[0] > 0: 
                    logger.warning(f'Duplicate records for {player} on {team} exist within Players table')
                    continue
                # Insert
                c.execute('INSERT INTO Gamelogs (Player, Season, PTS, Date, Team, Opponent, Away, Result, Win, Minutes, Started, Age, Playoff, FG, FGA, FGP, THP, THPA, THPP, FT, FTA, FTP, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, GmSc, PM) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', data)
            # DB Disconnect
            conn.commit()
        except Exception as err: print(f"Error: {err}")
        finally: # Close the connection when done
            if 'connection' in locals():
                conn.close()
                print("Connection closed")    
    
def save_career(career_stats):
    '''Populate the Career table'''
    with lock:
        try:
            conn = sql.connect(host=host, user=user, password=password, database=database)
            c = conn.cursor()
            for season, age, team, lg, pos, g, gs, mp, fg, fga, fgp, thp, thpa, thpp, tp, tpa, tpp, efg, ft, fta, ftp, orb, drb, reb, ast, stl, blk, tov, pf, pts, player in career_stats:
                
                # Convert formats where necessary and re-org
                data = (player, season, round(age, 3), team, pos, g, gs, round(mp,2), pts, fg, fga, round(fgp*100,3), tp, tpa, round(tpp*100,3), thp, thpa, round(thpp*100,3), round(efg*100,3), ft, fta, round(ftp*100,3), orb, drb, reb, ast, stl, blk, tov, pf)
                # Prevent inserting duplicates
                c.execute('SELECT COUNT(*) FROM Career WHERE Player = %s AND Season = %s', (player, season))
                if c.fetchone()[0] > 0: 
                    logger.warning(f'Duplicate records for {player} on {season} exist within Career table')
                    continue
                c.execute('INSERT INTO Career (Player, Season, Age, Team, Position, Played, Started, Minutes, PTS, FG, FGA, FGP, TP, TPA, TPP, THP, THPA, THPP, EFG, FT, FTA, FTP, ORB, DRB, TRB, AST, STL, BLK, TOV, PF) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', data)
            
            conn.commit()
        except Exception as err: print(f"Error: {err}")
        finally: # Close the connection when done
            if 'connection' in locals():
                conn.close()
                print("Connection closed")    

def save_playoffs(season, teams):
    '''Populate the Playoffs table'''
    with lock:
        try:
            conn = sql.connect(host=host, user=user, password=password, database=database)
            if conn.is_connected():
                c = conn.cursor()
                for team in teams:

                    print(season, team)
                    c.execute('SELECT COUNT(*) FROM Playoffs WHERE Team = %s AND Season = %s', (team, season))
                    # Use query to prevent inserting duplicates (by making sure there is no count of that log)
                    if c.fetchone()[0] <= 0:# Insert
                        c.execute('INSERT INTO Playoffs (Team, Season) VALUES (%s, %s);', (team, season))
                        continue
                    logger.warning(f'Duplicate records for {team} on {season} exist within Playoffs table')

                conn.commit()
        except Exception as err: print(f"Error: {err}")
        finally: # Close the connection when done
            if 'connection' in locals():
                conn.close()
                print("Connection closed")    

def save_teams(season, teams):
    '''Populate the Teams table'''
    with lock:
        try: 
            conn = sql.connect(host=host, user=user, password=password, database=database)
            if conn.is_connected():
                c = conn.cursor()
                for tag, team in teams:

                    # Prevent duplicate insertion (check existence)
                    c.execute("SELECT COUNT(*) FROM Teams WHERE Team = %s AND Tag = %s", (team, tag))
                    if c.fetchone()[0] <= 0: # Insert (record does not exist)
                        c.execute('INSERT INTO Teams (Team, Tag, Start, End) VALUES (%s, %s, %s, %s);', (team, tag, season, season))
                        continue
                    # Update 'start' season
                    c.execute("SELECT COUNT(*) FROM Teams WHERE Team = %s AND Tag = %s AND Start > %s", (team, tag, season))
                    if c.fetchone()[0] > 0:
                        c.execute('UPDATE Teams SET Start = %s Where Team = %s AND Tag = %s', (season, team, tag))
                        continue
                    # Update 'end' season
                    c.execute("SELECT COUNT(*) FROM Teams WHERE Team = %s AND Tag = %s AND End < %s", (team, tag, season))
                    if c.fetchone()[0] > 0:
                        c.execute('UPDATE Teams SET End = %s Where Team = %s AND Tag = %s', (season, team, tag))
                        continue
                    # No update/insert, duplicate error
                    logger.warning(f'Duplicate records for {team} exist within Teams table')

            conn.commit()
                
        except Exception as err: print(f"Error: {err}")
        finally: # Close the connection when done
            if 'connection' in locals():
                conn.close()
                print("Connection closed")    
