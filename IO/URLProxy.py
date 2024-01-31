# Name : URLProxy.py
# Auth : KT
# Date : 1/25/2024
# Desc : Implimentation of rotating proxy functionality on top of the requests module
import json                     # User credential file
import random                   # Random proxy generation
import time                     # Pause between requests
from requests import Session    # Session

session = Session() # Maintain single session to (substantially) increase sequential request speed 
file_path = 'IO/credentials.json'
credentials, IPs, headers = None, None, None
Bad_IPs = {}

def set_credentials_fpath(fpath): 
    global file_path
    file_path = fpath

def socks_credentials():
    '''Reads JSON file to load alternative HTML headers, Socks5 proxies, & proxy credentials (user:pass)'''
    # Open credentials file at specified filepath (default: './IO/credentials.json')
    with open(file_path, "r") as c:
        data = json.load(c)
        credentials = data['credentials'][0]   # Socks5 proxy credentials
        headers = [header for header in data['headers']]        # Alternative browser headers
        proxies = [proxy for proxy in data['proxies']]          # Alternative proxies
    return credentials, proxies, headers

while not credentials:
    try: credentials, IPs, headers = socks_credentials()
    except FileNotFoundError:
        proper = input('Please input the correct path to credentials.json:\n')
        set_credentials_fpath(proper)

def get(url, tries = 5):
    '''Returns a web request using randomly-chosen Socks5 proxies until 1 works'''
    # Instantiate variables
    global IPs, Bad_IPs                                         # Manage IP's outside of function scope
    IP, agent = random.choice(IPs), random.choice(headers)      # Random IP, HTML Header
    proxy = "socks5h://" + credentials + '@' + IP + ":1080"     # Combine
    start_time = time.time()
    fails = 0
    # Try connection
    r = -1
    while r == -1:
        try: r = session.get(url, proxies={'http':proxy, 'https':proxy}, headers={'User-Agent':agent}, timeout=10) # Request
        except Exception as err: 
            # Connection failure
            print(f"Error: (IP: {IP}) - Request Failed: {err}")
            # Add broken IP to list
            if not Bad_IPs.get(IP, None): Bad_IPs[IP] = 0
            # Delete broken proxies that meet timeout threshold
            Bad_IPs[IP] += 1
            if Bad_IPs.get(IP) == tries: 
                print(f'Deleting {IP} from working IP dict')
                IPs.remove(IP)
                # All proxes have timed out
                if len(IPs) == 0:
                    print('All proxies have timed out, clearing Bad_IPs cache')
                    IPs = list(Bad_IPs.keys())
            # Refresh new proxy
            IP, agent = random.choice(IPs), random.choice(headers)
            proxy = "socks5h://" + credentials + '@' + IP + ":1080"
            fails += 1
            time.sleep(1)
    # Connection success
    duration = time.time() - start_time
    print(f'Success (IP: {IP})\tRuntime: {duration} sec.\tAdjusted ({fails} failures): {duration - fails} sec.')
    return r.text