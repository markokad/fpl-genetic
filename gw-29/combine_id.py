# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:10:16 2020

@author: Marko
"""

import numpy as np
import pandas as pd 
#import matplotlib.pyplot as plt 
#from collections import Counter 
from unidecode import unidecode
import os
def choose_gw():
    df = pd.read_csv("GLK.csv")
    names = df.columns.to_list()
    temp = {}
    for i,n in enumerate(names):
        if n.isdigit():
            temp[int(n)]= names[i+1]
    print('Choose one of the following gameweeks: ')
    for k in temp.keys():
        print(k, ' ', end = '')
    while True:
        try:
            x = int(input('Enter gameweek number: '))
            if x in temp.keys():
                print('Selected gameweek ',x)
                break
            else:
                print('Choose only from available gameweeks')
        except ValueError:
            print('Need integer number')
        except:
            print('unexptected error')
            break
    return temp[x]
def combine_players_id(gw = 'Average'):
    print('[INFO] APPLYING ID LIST TO PREDICTION DATAFRAME - - ')
    glk = pd.read_csv("GLK.csv")
    dfd = pd.read_csv("DEF.csv")
    mid = pd.read_csv("MID.csv")
    fwd = pd.read_csv("FWD.csv")
    
    ## CHANGE DUPLICATE NAMES
    df_pedro = mid.index[(mid['last_name']=='Pedro') & (mid['Team']=='CHE')]
    mid.at[df_pedro,'first_name']= ' Ledesma'
    df_bruno = mid.index[(mid['last_name']=='Fernandes') & (mid['Team']=='MUN')]
    mid.at[df_bruno,'first_name']= ' Bruno'
    df_gedson = mid.index[(mid['last_name']=='Fernandes') & (mid['Team']=='TOT')]
    mid.at[df_gedson,'first_name']= ' Gedson'
    df_gabriel = fwd.index[(fwd['last_name']=='Jesus') & (fwd['Team']=='MCI')]
    fwd.at[df_gabriel,'first_name']= ' Gabriel'
    df_rosa = mid.index[(mid['last_name']=='Rosa') & (mid['Team']=='WHU')]
    mid.at[df_rosa,'first_name']= ' Bernardo Costa Da'
    df_berbha = dfd.index[(dfd['last_name']=='Bernardo') & (dfd['Team']=='BHA')]
    dfd.at[df_berbha,'first_name']= ' Fernandes da Silva Junior'
    
    ## SELECT COLUMNS OF INTEREST
    names = glk.columns.to_list()
    index = names[0:3]+[gw]+['Price'] 
    def convert_dataframe(a):
        a = a[index]
        a['Price'] =a['Price'].str[1:] # remove pound symbol from price 
        a['Price']=a['Price'].astype(float) # convert price from string to float 
        a = a.replace(np.nan, '',regex = True)   # NaN values in names convert to ''
        for col in names[:2]:
            a[col] = a[col].apply(unidecode)  # remove name accents for manual search 
        mask = a['first_name'] == '' 
        a['name']='' # make new column
        a['first_name']=a['first_name'].str[1:]
        a['name'][~mask] =a['first_name'] + ' ' + a['last_name']   # has first name 
        a['name'][mask] = a['last_name'] # no first name 
        cols = a.columns.to_list()
        cols = cols[-1:] + cols[:-1]
        a = a[cols]
        return a
    glk,dfd,mid,fwd = [convert_dataframe(a) for a in (glk,dfd,mid,fwd)]
    glk['Pos'] = 'G'
    dfd['Pos'] = 'D'
    mid['Pos'] = 'M'
    fwd['Pos'] = 'F'
    all_p = [glk,dfd,mid,fwd]
    df = pd.concat(all_p, ignore_index = True)
    df= df.rename(columns = {gw:'Average'})
    
    ## GET IDLIST
    dfid = pd.read_csv('player_idlist.csv')
    names_id = dfid.columns.to_list()
    dfid = dfid.replace(np.nan, '',regex = True)   # NaN values in names convert to ''
    for col in names_id[:2]:
        dfid[col] = dfid[col].apply(unidecode)  # remove name accents for manual search 
    dfid['name']= dfid['first_name']+' '+dfid['second_name']
    
    ##   make sets of unique values
    set1 = set(df['name'])
    set2 = set(dfid['name'])
    ##   set1 intersection set2 - give ID's from IDLIST 
    df['id']=0
    set12 = set1.intersection(set2)
    for row in df.itertuples():
        if row[1] in set12: # row = index, name,...
            string = row[1]
            df.at[row.Index, 'id']= dfid.loc[dfid['name']==string]['id']
    
    ## IF THEY DONT INTERSECT, BUT NAME IS SUBSTRING OF SET2 (example KEPA in KEPA ARRIZABALAGA)
    list12 = list(set1-set2)
    list21 = list(set2-set1)
    mapp = []
    for i,l12 in enumerate(list12):
        for j,l21 in enumerate(list21):
            if l12 in l21:
                mapp.append((i,j))
                break
    for i in mapp:
        df_name = list12[i[0]]
        dfid_name = list21[i[1]]
       # df.loc[df['name']==df_name, ['id']] = dfid.loc[df['name']==dfid_name]['id']
        df_index = df.index[df['name']==df_name]
        dfid_index = dfid.index[dfid['name']==dfid_name].values
        idd = dfid.loc[dfid_index]['id']
        idd = idd.to_numpy()
        df.at[df_index,'id'] = idd
       # print(idd,'**',list12[i[0]],'---', list21[i[1]])    
        
    ## OTHER NAMES HAVE TO BE GIVEN MANUALLY 
    templist = []
    for i in mapp:
        templist.append(list21[i[1]])
    set_did = set(templist)
    set_to_do = (set2-set1)-set_did
    list_dfid_to_do = list(set_to_do)
    list_df_to_do = ['Cuco Martina','Lucas Moura','Xande Silva','Andre Gomes','Chicharito','Gedson Fernandes','Bruno Fernandes',\
    'Angelino','Joselu','Trezeguet','Fernandinho','Baston','Kiko Femenia','Gabriel Jesus','Jorginho','Ki Sung-yueng',\
    'Bernardo Silva', 'Jota','Fernandes da Silva Junior Bernardo','Ledesma Pedro','Jonny','Fabinho']
    # PRINT THEM  TO VISUALLY CONFIRM
    
    #for x,y in zip(list_df_to_do, list_dfid_to_do):
    #    print("{:<40}{:<50}".format(x,y))
    
    for i in range(len(list_df_to_do)):
        df_name = list_df_to_do[i]
        dfid_name = list_dfid_to_do[i]
       # df.loc[df['name']==df_name, ['id']] = dfid.loc[df['name']==dfid_name]['id']
        df_index = df.index[df['name']==df_name]
        dfid_index = dfid.index[dfid['name']==dfid_name].values
        idd = dfid.loc[dfid_index]['id']
        idd = idd.to_numpy()
        df.at[df_index,'id'] = idd
        
     ## SAVE DF to CSV 
    df.to_csv('players_with_id.csv')
    print('[INFO] ID LIST TO PREDICTION DATAFRAME APPLIED- SAVED AS players_with_id.csv ')
    