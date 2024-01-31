# NBA-Visualizer
## Author: Kareem T | Date: 11/22/2022

Program that utilizes web-scraping (via basketball-reference.com) to construct DataFrames, populate a database, and host a Web-API

**The goal:** Find analytical insights about the NBA.

Both the dataframe web-scraping and database populator modules are included in ./IO.
SQL is default but you can modify IO/DB.py to use any connector given you also change the functions.

If you are creating a database, you will need a SockS5 proxy and browser headers to avoid request limits; follow the 'Data Web-Scrape Instructions' below.

If you are only creating a select few dataframes, you do not require a proxy.

## Features

- Retrieve up-to-date NBA player gamelogs, averages, and other information
- Cover statistics from any recorded season
- Creates Pandas DataFrames for simple data manipulation, analysis, visualization, etc.
- MySQL database creation & query functionality
- Web-API for data retrieval: https://visnba.com
- Built-in proxy (SockS5) compatibility (**Highly recommended** for web-scraping / db creation)

## Use Instructions
##### *Store/Query Database*
1. Setup your database connector & credentials in 'IO/DB.py'
   - The module is setup for SQL (mySQL) by default: different connectors require the functions to be changed.
2. Use the 'query()' function in 'IO/DB.py' to pass SQL queries
   - Import DB.py and call query()
3. Use the 'save_[operation]' functions in 'IO/DB.py' to store into the database

##### *Data Web-Scrape Instructions*
**Highly recommended: Use bundled Python module (URLProxy.py) that uses a Socks5 proxy. Set 'Proxy = True' in Main.Multi_Process()**

0. (If using proxy) Create a JSON file in the IO directory named 'credentials.json' with the following format
{
    "credentials": ["Socks5 user:Socks5 pass"]
    "headers": [Browser headers]
    "proxies": [IP addresses]
}
1. Use Functions in 'IO/WebScraper.py' to generate DataFrames
2. Pass the '.values' attribute of the DataFrames to 'IO/DB.py' functions to save them to the db (e.g., db.save_gamelogs(df.values))

## About

This project began as a Jupyter notebook about betting analytics but has since been expanded to separate modules.

I am an amateur wanting to gauge my abilities at making a data retrieval method if I could not access an API (The NBA removed their API a few years ago).

I host my own API with data retrieved using these modules here: (https://visnba.com); feel free to use these modules to create a platform of your own.

## Legal
This tool is in no ways endorsed by the National Basketball Association (NBA) or basketball-reference.com