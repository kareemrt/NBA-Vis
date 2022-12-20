# NBA-Visualizer
## Author: Kareem T | Date: 11/22/2022
Program that uses basketball-reference.com & web-parsing to construct Pandas Dataframe and find analytical insights about the NBA.

**As of 11/29, functionality includes:**
* Parsing CSV files for NBA 2022 averages data within DataFrames
* Parsing 1+ current (2022) player's season stats (df) from averages df
* Parsing 1+ players (df) specified stats from averages df
* Visualizing 1+ players' season OR specified stats (graph) 

**As of 12/11, functionality includes:**
* Pulling players' UUID from BasketballReference.com
* Pulling teams' UUID from BasketballReference.com
* Pulling players' career stats from BBREF given UUID
* Pulling players' gamelogs from BBREF given UUID
* Separate module for functions: methods.py
* Separate module for tests: tests.py
* Separate module for Object-Oriented implementation: OO.py

**As of 12/20, functionality includes:**
* File Input/Output functionality to save Player & Team urls, and user League/Team/Player objects (Separate module: File_IO.py)
* Developed Object-Oriented implimentation to abstract out pulling/storing user data (Separate module: OO.py (old) -> Objects.py)
* Developed Unittests for more up-to-date testing
* Abstract out methods.py -> functions.py & HTML_IO.py
* Abstract out Data files (/Data) and IO files (/IO)
