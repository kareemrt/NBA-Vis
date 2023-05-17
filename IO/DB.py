# Name : DB.py
# Auth : KT
# Desc : Module that interacts with SQLite database
import sqlite3 as sql
import logging
import IO.WebScraper as WS

logger = logging.getLogger()
file_handler = logging.FileHandler('Logs/net.log', encoding='utf-8', mode='a'); file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')); file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

def query(query):
    '''SQL query'''
    conn = sql.connect('NBA.db')
    c = conn.cursor()
    c.execute(query)
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return rows

def save_players(player, tag, team):
    '''Populate the players table'''
    # DB Connect
    conn = sql.connect('NBA.db')
    c = conn.cursor()
    # Use query to prevent inserting duplicates (by making sure there is no count of that log)
    if c.execute('SELECT COUNT(*) FROM Players WHERE Player = ? AND Team = ?', (player, team)).fetchone()[0] > 0:
        logger.warning(f'Duplicate records for {player} on {team} exist within Players table')
    else: # Insert
        c.execute('INSERT INTO Players (Player, Tag, Team) VALUES (?, ?, ?);', (player, tag, team))
    # DB Disconnect
    conn.commit()
    conn.close()

def save_gamelogs(gamelogs):
    '''Save a np matrix of gamelogs into the SQLite DB, log-by-log'''
    # DB Connect
    conn = sql.connect('NBA.db')
    c = conn.cursor()
    # Iterate log by log
    for date, age, team, away, opp, res, gs, mp, fg, fga, fgp, tp, tpa, tpp, ft, fta, ftp, orb, drb, reb, ast, stl, blk, tov, pf, pts, gmsc, pm, season, player in gamelogs:
        # Convert formats where necessary and put in correct order
        data = (player, season, pts, date, team, opp, int(away), res, int(res>0), round(mp,2), gs, round(age,3), fg, fga, round(fgp*100,3), tp, tpa, round(tpp*100,3), ft, fta, round(ftp*100,3), orb, drb, reb, ast, stl, blk, tov, pf, gmsc, pm)
        # Use query to prevent inserting duplicates (by making sure there is no count of that log)
        if c.execute('SELECT COUNT(*) FROM Gamelogs WHERE Player = ? AND Date = ?', (player, date)).fetchone()[0] > 0: 
            logger.warning(f'Duplicate records for {player} on {team} exist within Players table')
            continue
        # Insert
        c.execute('INSERT INTO Gamelogs (Player, Season, PTS, Date, Team, Opponent, Away, Result, Win, Minutes, Started, Age, FG, FGA, FGP, THP, THPA, THPP, FT, FTA, FTP, ORB, DRB, TRB, AST, STL, BLK, TOV, PF, GmSc, PM) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
    # DB Disconnect
    conn.commit()
    conn.close()
    
def save_career(career_stats):
    '''Populate the Career table'''
    # DB Connect
    conn = sql.connect('NBA.db')
    c = conn.cursor()
    # Iterate log by log
    for season, age, team, lg, pos, g, gs, mp, fg, fga, fgp, thp, thpa, thpp, tp, tpa, tpp, efg, ft, fta, ftp, orb, drb, reb, ast, stl, blk, tov, pf, pts, player in career_stats:
        # Convert formats where necessary and put in correct order
        data = (player, season, round(age, 3), team, pos, g, gs, round(mp,2), pts, fg, fga, round(fgp*100,3), tp, tpa, round(tpp*100,3), thp, thpa, round(thpp*100,3), round(efg*100,3), ft, fta, round(ftp*100,3), orb, drb, reb, ast, stl, blk, tov, pf)
        # Use query to prevent inserting duplicates (by making sure there is no count of that log)
        if c.execute('SELECT COUNT(*) FROM Career WHERE Player = ? AND Season = ?', (player, season)).fetchone()[0] > 0: 
            logger.warning(f'Duplicate records for {player} on {season} exist within Career table')
            continue
        # Insert
        c.execute('INSERT INTO Career (Player, Season, Age, Team, Position, Played, Started, Minutes, PTS, FG, FGA, FGP, TP, TPA, TPP, THP, THPA, THPP, EFG, FT, FTA, FTP, ORB, DRB, TRB, AST, STL, BLK, TOV, PF) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
    # DB Disconnect
    conn.commit()
    conn.close()

def save_teams(teams):
    '''Populate the Teams table'''
    # DB Connect
    conn = sql.connect('NBA.db')
    c = conn.cursor()
    for team, url in teams.items():
        # Use query to prevent inserting duplicates (by making sure there is no count of that log)
        if c.execute('SELECT COUNT(*) FROM Teams WHERE Team = ? AND URL = ?', (team, url)).fetchone()[0] > 0:
            logger.warning(f'Duplicate records for {team} exist within Teams table')
        else: # Insert
            c.execute('INSERT INTO Teams (Team, URL) VALUES (?, ?);', (team, url))
    # DB Disconnect
    conn.commit()
    conn.close()
