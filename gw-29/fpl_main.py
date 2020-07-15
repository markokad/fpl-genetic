# -*- coding: utf-8 -*-
"""
Created on Mon Mar  9 15:39:52 2020

@author: marko
"""

from Fetch_projections_overlord import *
from make_raw import *
import combine_id 
from team_info import *
import ga

import sys
import pandas as pd 
import warnings

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
    
 
def main():
    warnings.filterwarnings("ignore")
    q = query_yes_no("Do you want to fetch data from overlord?", None)
    if q:
        fetch_from_overlod() 
    else:
        print('Asuming overlord data is in folder (GLK,DEF,MID,FWD)')
     # make and get  raw data 
    
    data = get_data()
    players = data['elements']
    parse_players(players)
    del players   
    q = query_yes_no("Do you want to create new predictions csv with selected gameweek?", None)
    if q:
        gw  = combine_id.choose_gw()
        combine_id.combine_players_id(gw)
    else:
        print('Asuming players_with_id.csv exists')
    print('Next action is loading data from players_with_id.csv')
    print('If u want, you can change predictions in csv file, then load when ready')
    while True:
        q = query_yes_no("Are you ready to continue (load players_with_id.csv)", None)
        if q:
            df = pd.read_csv('players_with_id.csv')
            break
        else:
            print('Yes is the only way forwards')
            
            
 
    while True:
        try:
            x = int(input('Enter your team ID '))
            break
        except ValueError:
            print('Invalid input (put INT code of team)')
        except :
            print('Unexpted error')
            break
    team_id = x
    team_dict,budget = get_team_info(team_id)
    for keys,values in team_dict.items():
        df_index = df.index[df['id']==keys].to_numpy()[0]
        values /=10
        df.at[df_index,'Price'] = values
    print("Prices adjusted. Effective budget = ", budget)
    ga.budget = budget
    
    gen_alg = ga.GeneticAlgorithm(df, population_size=1000,generations=50, elitism = 1)
    q = query_yes_no("Bench boost - (YES for BENCHBOOST, NO for just 11 players)", None)
    if q:
        gen_alg.fitness_function = ga.fitness_bb
    else:
        gen_alg.fitness_function = ga.fitness
    
    print('Starting genetic algorithm ')
    gen_alg.run()
    print('Genetic algorithm finished')
    max_points,team_keys = ga.form_best_team(gen_alg.best_individual()[1])
    ga.print_best(gen_alg,max_points , team_keys)
    
if __name__ == '__main__':
    main()

    