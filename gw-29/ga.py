# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 16:34:50 2020

@author: Marko
"""
import sys
import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt 
from collections import Counter 
from unidecode import unidecode
import os
import copy 
from operator import attrgetter 
from six.moves import range
import random
#import FPL_project 
# sort gk 
# sort def
# sort mid
# sort fwd
# team form 1 3 0 1 
# sort others not selected 
# chose best 6 from others
# add captain 
budget = 0 
categories = ['G1','G2','D1','D2','D3','D4','D5','M1','M2','M3','M4','M5','F1','F2','F3']
def fitness(individual):
    currentPrice = 0
    points = 0
    value_list = list(individual.values())
    points_list = []
    team_list = []
    for v in value_list:
        currentPrice += v[2] # price location
        points_list.append(v[1])
        team_list.append(v[3])
    if currentPrice > budget:
        return 0
    
    c =Counter(team_list)
    if max(c.values()) > 3 :
        return 0
 #   points_list =value_list[1] # points list 
  #  print('points_list ', points_list )
    d = dict(zip(individual.keys() , points_list))
    d = {k: v for k, v in sorted(d.items(), key = lambda item: item[1], reverse = True)} # sort player by expected points
    keys = list(d.keys())     # changeable copy of keys from the dict sorted by values
    chosen = []   # lineup, first 11 are in a team 
  #  print('dict = ',d)
    for l in keys:
        if l[0]=='G':
            chosen.append(l)
            points+= d.pop(l)
            keys.remove(l)
            break

    defs = 0 
    while defs < 3:
        for l in keys:
            if l[0]=='D':
                chosen.append(l)
                points+=d.pop(l)
                keys.remove(l)
                break
        defs +=1
    for l in keys:
        if l[0]=='F':
            chosen.append(l)
            points+= d.pop(l)
            keys.remove(l)
            break
    chosen+= keys
    for l in chosen[1:]:   # put gk last 
        if l[0]=='G':
            l_h = l
            chosen.remove(l)
            chosen.append(l_h)
            break
    # nov chosen[5:11] are key values to points 
    for c in chosen[5:11]:
        points += d[c]
 #   print('chosen are ', chosen)
    points += max(points_list) # captain 
    return points
def fitness_bb(individual):
    currentPrice = 0
    points = 0
    value_list = list(individual.values())
    points_list = []
    team_list = []
    for v in value_list:
        currentPrice += v[2] # price location
        points_list.append(v[1])
        team_list.append(v[3])
    if currentPrice > budget:
        return 0
    
    c =Counter(team_list)
    if max(c.values()) > 3 :
        return 0
    for p in points_list:
        points += p 
    points += max(points_list) # captain
    return points
class GeneticAlgorithm(object):
    # main class of Genetic algorithm 
    def __init__(self,
                seed_data,
                generations = 100,
                population_size=100,
                crossover_probability=0.8,
                mutation_probability = 0.15,
                elitism = True,
                maximise_fitness = True,
                ):
        self.seed_data = seed_data    # pandas input of genetic alg
        self.population_size = population_size
        self.generations = generations
        self.crossover_probability = crossover_probability
        self.mutation_probability = mutation_probability
        self.elitism = elitism
        self.maximise_fitness = maximise_fitness # minimise or maximise fitness  - True for max, False for min 
        self.categories = ['G1','G2','D1','D2','D3','D4','D5','M1','M2','M3','M4','M5','F1','F2','F3']
        self.current_generation = []
        self.fitnesshistory = np.zeros(1)
        self.current_best_individual = np.zeros(1)
        def create_individual(seed_data):
            previously_chosen = []
            # make dictionary of individuals 
            individuals = {gene: random_select(gene,seed_data,previously_chosen) for gene in self.categories}
            return individuals
        def random_select(key,seed_data,previously_chosen):
            # randomly select player from each category for initial lineup and check for duplicates (WR1 -WR2 and FLEX)
            already_chosen = True 
            while already_chosen:    # if player was already chosen 
                key = ''.join([i for i in key if not i.isdigit()])  # D1 => D ... are keys
   # not flex
                seed_data = seed_data[seed_data['Pos'].str.contains(key)].reset_index(drop= True) # same 
              #  print(len(seed_data))
                index = random.randrange(1,len(seed_data))
                value = (seed_data.get_value(index,'name'),seed_data.get_value(index,'Average'),\
                         seed_data.get_value(index,'Price'),seed_data.get_value(index,'Team'))
                if value[0] not in previously_chosen:
                    already_chosen = False  
                    previously_chosen.append(value[0]) # 
            return value 

        def crossover(parent1,parent2): 
            # from 2 parents returns tuple of 2 children 
            def are_there_duplicates(values):
                return len(set(values)) != len(values)  
            exist_duplicates = True 
            while exist_duplicates: 
                index = random.randrange(1,len(parent1))
                keys = list(parent1.keys())
                np.random.shuffle(keys)
                child1 = {key: (parent1[key] if i <= index else parent2[key])\
                          for key,i in zip(keys,range(len(self.categories)))}
                exist_duplicates = are_there_duplicates(child1.values())    # did same players merge from diff parents 

            exist_duplicates = True 
            while exist_duplicates: 
                index = random.randrange(1,len(parent2))
                keys = list(parent2.keys())
                np.random.shuffle(keys)
                child2 = {key: (parent2[key] if i <= index else parent1[key])\
                          for key,i in zip(keys,range(len(self.categories)))}
                exist_duplicates = are_there_duplicates(child2.values())    # did same players merge from diff parents 
            return child1,child2
        def mutate(individual,seed_data):
            mutation_index = random.randrange(len(individual))
            keys = list(individual.keys())
            mut_keys = keys[mutation_index] # mutate just this 1 key 
            previously_chosen = [individual[key][0] for key in keys if key != mut_keys]    # did mutate result in duplicate
            individual[mut_keys] = random_select (mut_keys,seed_data,previously_chosen)  # mutate - duplicate ? 

        def tournament(population):
            tournament_size = self.population_size // 10
            competitors = random.sample(population, tournament_size) # random sample takes population as set 
            competitors.sort(key = attrgetter('fitness'), reverse = self.maximise_fitness)  # reverse = True => descending 
            return competitors[0]    # take the best 
# since this functions appear in __init__, need to make them available for other functions in class
        self.mutate = mutate
        self.tournament = tournament
        self.create_individual = create_individual
        self.crossover = crossover
    def create_initial_population(self):
        # first genration 
        initial_population = []
        for _ in range(self.population_size):
            genes = self.create_individual(self.seed_data) # create individual of 9 position, as in 1 team
            individual = Chromosome(genes)
            initial_population.append(individual)
        self.current_generation = initial_population
    def calculate_population_fitness(self):
        total = 0 
        for individual in self.current_generation:
            individual.fitness = self.fitness_function(individual.genes)
            total += individual.fitness
        total /= self.population_size
        self.fitnesshistory = np.append(self.fitnesshistory, total)
        
    def rank_population(self): # this functions sorts population, by default descending
        self.current_generation.sort(key = attrgetter('fitness'),reverse = self.maximise_fitness) 
    def create_new_population (self):
        new_population = []
        elite = copy.deepcopy(self.current_generation[0]) # do we use elitism, must use deepcopy,not shallow
        
        while len(new_population) < self.population_size:
            parent1 = copy.deepcopy(self.tournament(self.current_generation))
            parent2 = copy.deepcopy(self.tournament(self.current_generation))
            
            child1,child2 = parent1, parent2
            child1.fitness, child2.fitness = 0,0
            
            if np.random.rand() < self.crossover_probability : # does it crossover, if not child = parent 
                child1.genes,child2.genes = self.crossover(parent1.genes, parent2.genes)
            if np.random.rand() < self.mutation_probability : 
                self.mutate(child1.genes, self.seed_data)
            if np.random.rand() < self.mutation_probability :
                self.mutate(child2.genes, self.seed_data)
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2) # if population is odd number 
        if self.elitism:
            new_population[0] = elite 
        self.current_generation = new_population
    
    def create_first_generation(self): 
        self.create_initial_population()
        self.calculate_population_fitness()
        self.rank_population()
    def create_next_generation(self): 
        self.create_new_population()
        self.calculate_population_fitness()
        self.rank_population()
    def run(self):
        self.create_first_generation()
        self.current_best_individual = np.append(self.current_best_individual, self.best_individual()[0])
        n = self.generations
        mark = int(np.floor(n/20))
        bar = 0
        for i in range(1,self.generations):
            self.create_next_generation()  # fitness is updated in calculate fitness
            self.current_best_individual = np.append(self.current_best_individual, self.best_individual()[0])
            if i % mark ==0 and 5*bar<100:
                bar +=1
                sys.stdout.write('\r')
                sys.stdout.write("[%-20s] %d%%" % ('='*bar,5*bar))
                sys.stdout.flush()
            
        self.fitnesshistory = np.delete(self.fitnesshistory,[0]) # delete first 0         
        self.current_best_individual = np.delete(self.current_best_individual, [0])
    def best_individual(self):
        best_individual_ = self.current_generation[0]
        return  (best_individual_.fitness, best_individual_.genes)# returns best individuals  
    #### best individual not finished 
    def last_generation(self):
        return ((competitor.fitness, competitor.genes) for competitor in self.current_generation)
    
class Chromosome(object): 
    def __init__(self,genes):
        self.genes = genes 
        self.fitness = 0 
        
# sort gk 
# sort def
# sort mid
# sort fwd
# team form 1 3 0 1 
# sort others not selected 
# chose best 6 from others
# add captain 
def form_best_team(individual):
    currentPrice = 0
    points = 0
    value_list = list(individual.values())
    points_list = []
    team_list = []
    for v in value_list:
        currentPrice += v[2] # price location
        points_list.append(v[1])
        team_list.append(v[3])
    if currentPrice > budget:
        return 0
    
    c =Counter(team_list)
    if max(c.values()) > 3 :
        return 0
 #   points_list =value_list[1] # points list 
  #  print('points_list ', points_list )
    d = dict(zip(individual.keys() , points_list))
    d = {k: v for k, v in sorted(d.items(), key = lambda item: item[1], reverse = True)} # sort player by expected points
    keys = list(d.keys())     # changeable copy of keys from the dict sorted by values
    chosen = []   # lineup, first 11 are in a team 
  #  print('dict = ',d)
    for l in keys:
        if l[0]=='G':
            chosen.append(l)
            points+= d.pop(l)
            keys.remove(l)
            break

    defs = 0 
    while defs < 3:
        for l in keys:
            if l[0]=='D':
                chosen.append(l)
                points+=d.pop(l)
                keys.remove(l)
                break
        defs +=1
    for l in keys:
        if l[0]=='F':
            chosen.append(l)
            points+= d.pop(l)
            keys.remove(l)
            break
    chosen+= keys
    for l in chosen[1:]:   # put gk last 
        if l[0]=='G':
            l_h = l
            chosen.remove(l)
            chosen.append(l_h)
            break
    # nov chosen[5:11] are key values to points 
    for c in chosen[5:11]:
        points += d[c]
 #   print('chosen are ', chosen)
    points += max(points_list) # captain
    first11 = []
    chosen11 = chosen[:11] # faster to form it once 
    for c in categories:
        if c in chosen11:
            first11.append(c)
    for c in chosen[11:]:
        first11.append(c)
    return points,first11
def print_best(gen_alg,max_points, team_keys):
    print("{:<10}{:<30}{:<20}{:<20}{:<20}".format('pos','name','points','price','team'))
    for b,t in enumerate(team_keys):
        e = gen_alg.best_individual()[1][t]
        print("{:<10}{:<30}{:<20}{:<20}{:<20}".format(t,e[0],e[1],e[2],e[3]))
        if b==10:
            print('-'*90)
    print('Expected points :' , max_points)

