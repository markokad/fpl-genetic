# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:04:29 2020

@author: Marko
"""

import requests
import json
import time
import os 
import csv

def get_data():
    """ Retrieve the fpl player data from the hard-coded url
    """
    response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    responseStr = response.text
    data = json.loads(responseStr)
    return data
def extract_stat_names(dict_of_stats):
    """ Extracts all the names of the statistics
    Args:
        dict_of_stats (dict): Dictionary containing key-alue pair of stats
    """
    stat_names = []
    for key, val in dict_of_stats.items():
        stat_names += [key]
    return stat_names

def parse_players(list_of_players):
    print('[INFO] Fetching raw player data')
    stat_names = extract_stat_names(list_of_players[0])
    filename =  'players_raw.csv'
    f = open(filename, 'w+', encoding='utf8', newline='')
    w = csv.DictWriter(f, sorted(stat_names))
    w.writeheader()
    for player in list_of_players:
            w.writerow({k:str(v).encode('utf-8').decode('utf-8') for k, v in player.items()})
    print('[INFO] Saved raw player data to "players_raw.csv"')
            

