# NBA-Visualizer
## Author: Kareem T | Date: 11/22/2022

Program that utilizes web-scraping (via basketball-reference.com) to construct DataFrames and populate an SQL database 

**The goal:** Find analytical insights about the NBA.

## About

This project began as a Jupyter notebook but the functionality has been expanded to separate modules so that it can be used in both Jupyter and as a standalone Python program.

I am an amateur software engineer and wanted to gauge my ability to make a functional 'hacky' data retrieval method if I did not have access to a clean API (The NBA removed their official API a few years ago).

I have bundled a complete SQLite database (NBA.db) of current NBA player gamelogs / averages for their entire careers (minus playoffs) so that you don't need to create it. If you wish to create your own database with these methods, you will need a SockS5 proxy to avoid HTTP request limits alongside some browser headers (which can simply be found online); with these, you would follow the instructions in the 'Proxy / DB Instructions' to create the necessary 'credentials.json' file necessary for IO/WebScraper.py to work.

## Functionality

- Retrieve up-to-date NBA player gamelogs & season averages
- Cover statistics from any recorded season
- Creates Pandas DataFrames for simple data manipulation, analysis, visualization, etc.
- SQLite database creation & query functionality
- Built-in proxy (SockS5) compatibility (**Required** for web-scraping / db creation)

## Use Instructions

1. Access the 'query()' function from the 'IO/DB.py' module to pass SQL queries

## Proxy / DB Instructions

**This functionality is meant to be used with a proxy because of HTTP request limits; I bundle a Python Wheel that wraps a SockS5 proxy ontop of the standard requests library get() function**

*To avoid using any proxies (NOT recommended), simply navigate to 'IO/WebScraper.py' and replace the 'URLProxy' library with 'requests', alongside subsequent calls to 'URLProxy.force_connect(url)' with requests.get(url)'*

1. Install the Wheel 'URLProxy-0.1-py2-py3-none-any.whl' via pip (e.g., pip install 'URLProxy-0.1-py2-py3-none-any.whl')
1. Create a JSON file in the IO directory named 'credentials.json' with the following format
{
    "credentials": [Socks5 user, Socks5 pass, Socks5 user:pass]
    "headers": [Browser headers]
    "proxies": [IP addresses]
}
2. Use Functions in 'IO/WebScraper.py' to generate DataFrames
3. Pass the '.values' attribute of the DataFrames to 'IO/DB.py' functions to save them to the SQLite db (e.g., db.save_gamelogs(df.values))

## DB Schema

1. Players (Player, Tag, Team)
2. Teams (Team, URL)
3. Career (Player, Season, Age, Team, Position, Played, Started, Minutes,...(game stats))
4. Gamelogs (Player, Season, PTS, Date, Team, Opponent, Away, Result, Win, Minutes, Started, Age,...(game stats))

## Legal
This tool is in no ways endorsed by the National Basketball Association (NBA) or basketball-reference.com