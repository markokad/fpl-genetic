# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:17:08 2020

@author: Marko
"""
import requests
import json
import time
import pandas as pd 
import numpy as np
from unidecode import unidecode
import os

def get_entry_transfers_data(entry_id):
    """ Retrieve the transfer data for a specific entry/team
    Args:
        entry_id (int) : ID of the team whose data is to be retrieved
    """
    base_url = "https://fantasy.premierleague.com/api/entry/"
    full_url = base_url + str(entry_id) + "/transfers/"
    response = ''
    while response == '':
        try:
            response = requests.get(full_url)
        except:
            time.sleep(5)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    data = json.loads(response.text)
    return data
def get_entry_gws_data(entry_id,num_gws):
    """ Retrieve the gw-by-gw data for a specific entry/team
    Args:
        entry_id (int) : ID of the team whose data is to be retrieved
    """
    base_url = "https://fantasy.premierleague.com/api/entry/"
    gw_data = []
    for i in range(1, num_gws+1):
        full_url = base_url + str(entry_id) + "/event/" + str(i) + "/picks/"
        response = ''
        while response == '':
            try:
                response = requests.get(full_url)
            except:
                time.sleep(5)
        if response.status_code != 200:
            raise Exception("Response was code " + str(response.status_code))
        data = json.loads(response.text)
        gw_data += [data]
    return gw_data
## GET FIRST TEAM INFO 
def get_team_info(team_id):
    print('[INFO] Getting team_info')
    gw = get_entry_gws_data(team_id,1)
    ## GET TRASNFER DATA 
    t = get_entry_transfers_data(team_id)
    ## READ PLAYERS RAW 
    raw = pd.read_csv('players_raw.csv')
    cols = raw.columns.to_list()
    cols = ['cost_change_start','now_cost','id','start_cost']
    raw['start_cost'] = raw['now_cost']-raw['cost_change_start']
    
    ## READ FIRST TEAM
    
    first_team = gw[0]['picks']
    
    ## MAKE DICT AND ITB FOR FIRST TEAM
    
    start_budget = 1000
    start_team_value =0
    team_dict = dict()
    for f in first_team:
        id_ = f['element']
        #print(raw.loc[raw['id']==id_]['start_cost'].to_numpy())
        start_team_value +=raw.loc[raw['id']==id_]['start_cost'].to_numpy()[0]
        team_dict[id_] = raw.loc[raw['id']==id_]['start_cost'].to_numpy()[0]
    itb = start_budget - start_team_value
    
    ## APPLY TRANSFERS  
    
    for transfer in reversed(t):
        player_in = transfer['element_in']
        in_cost = transfer['element_in_cost']
        player_out = transfer['element_out']
        out_cost = transfer['element_out_cost']
        team_dict[player_in]= team_dict.pop(player_out)#[player_out] # new key
        team_dict[player_in] = in_cost
        change = out_cost - in_cost
        itb += change
        
    ##ITB AND TEAM DICT calculated
    for k in team_dict.keys():
        in_cost = team_dict[k]
        now_cost = raw.loc[raw['id']==k]['now_cost'].to_numpy()[0]
        if now_cost <= in_cost:
            team_dict[k] = now_cost
        else:
            team_dict[k] += np.floor((now_cost-in_cost)/2)
    
    ## CALCULATE EFFECTIVE BUDGET 
    purchase_price = np.fromiter(team_dict.values(), dtype = float)
    purchase_price /=10
    itb /=10
    budget = sum(purchase_price) + itb
    print('[INFO] Team info loaded')
    return team_dict, budget 