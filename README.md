# NBA-Visualizer
## Author: Kareem T | Date: 11/22/2022
Program that can use either data files (csv/db) or web-parsing (via basketball-reference.com) to construct Pandas Dataframe and find analytical insights about the NBA.

This project began as a Jupyter notebook but the functionality has been expanded to separate modules so that it can be used in both Jupyter and as a standalone Python program.

**As of 11/29, functionality includes:**
* Parsing CSV files for NBA 2022 averages data within DataFrames
* Parsing 1+ current (2022) player's season stats (df) from averages df
* Parsing 1+ players (df) specified stats from averages df
* Visualizing 1+ players' season OR specified stats (matplotlib graph) 

**As of 12/11, functionality includes:**
* Pulling players' UUID from BasketballReference.com
* Pulling teams' UUID from BasketballReference.com
* Pulling players' career stats from BBREF given UUID
* Pulling players' gamelogs from BBREF given UUID
* Separate module for functions: methods.py
* Separate module for tests: tests.py
* Separate module for Object-Oriented implementation: OO.py

**As of 12/20, functionality includes:**
* File Input/Output functionality to save Player & Team urls, and user League/Team/Player objects (module: File_IO.py)
* Developed Object-Oriented implimentation to abstract out pulling/storing user data (module: OO.py (old) -> Objects.py)
* Developed Unittests for more up-to-date testing
* Abstract out methods.py -> functions.py, HTML_IO.py
* Abstract out Data files (/Data) and IO files (/IO)

**As of 12/29, functionality includes:**
* HTML I/O with proxy functionality to (semi) reliably web-scrape data on all the web-data gathering methods
* Abstract out credentials/proxies to File IO to promote modularity
* Cleaned unittest name scheme to more clearly organize and reflect testing purpose
* Added functionality for player stat visualization

**As of 1/16, functionality includes:**
* Added 'Group' Class to help compare specific players (not on the same team)
* Reduced # of object methods by ~1/3 to enhance clarity
* Abstract out html headers for IO requests to a file to promote modularity
* Cleaned up main.py and process.ipynb so that user use is straightforward
* Bug fixes
