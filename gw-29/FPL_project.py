# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:05:25 2020

@author: Marko
"""
from Fetch_projections_overlord import *
from make_raw import *
from combine_id import *
from team_info import *
import ga

import sys
import pandas as pd 
import warnings



def main():
    if len(sys.argv) != 2:
        print("Usage: python FPL_project.py  <team_id>. Eg: python FPL_project.py 5000")
        sys.exit(1)
        
    # disable warnings
    warnings.filterwarnings("ignore")
    team_id = int(sys.argv[1])  
    # fetch from overlod projections 
    ga.budget = 10 # test
    fetch_from_overlod()    
    # make and get  raw data     
    data = get_data()
    players = data['elements']
    parse_players(players)
    del players    
    # put id's to prediction csv     
    combine_players_id()       
    #get team info 
    team_dict,budget = get_team_info(team_id)
    df = pd.read_csv('players_with_id.csv')
    # MBWANA SAMATTA HAS UNREAL PREDICTION
    dfind = df.index[df['name']=='Mbwana Samatta'][0]
    df.at[dfind,'Average'] = 3.0 # manual adjust
    # 
    for keys,values in team_dict.items():
        df_index = df.index[df['id']==keys].to_numpy()[0]
        values /=10
        df.at[df_index,'Price'] = values
    print("Prices adjusted. Effective budget = ", budget)
    ga.budget = budget
    
    # import genetic 
    gen_alg = ga.GeneticAlgorithm(df, population_size=1000,generations=50, elitism = 1)
    gen_alg.fitness_function = ga.fitness
    print('Starting genetic algorithm ')
    gen_alg.run()
    print('Genetic algorithm finished')
    max_points,team_keys = ga.form_best_team(gen_alg.best_individual()[1])
    ga.print_best(gen_alg,max_points , team_keys)
    
if __name__ == '__main__':
    main()