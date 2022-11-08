import numpy as np
import random
import mesa
import plants
import data
from typing import Type

class ElecCo(mesa.Agent):
    '''
    Agent. Starts with powerplants and money. Using predictions of future elec. prices and fuel costs, will choose if and what
    to invest in -> not implemented. 
    Currently just choses whether to invest or not.  
    '''
    def __init__(self, name: str, plants:list[plants.PowerPlant] = None, cash: str = 0):
        '''
        electricity company definition
        name: unique name 
        initial_plants: power plants that it is initialised with
        cash: amount of money it starts with
        '''
        self.name = name
        self.plants = plants
        self.cash = cash


    def invest(self, strike_price: float, buildable_plants: list[Type[plants.PowerPlant]]):
        '''
        If plant lcoe is lower than strike price, build it.
        In future, ,ore checks whether it would be profitable and choose the best one to build    
        '''
        viable_plants = []
        for plant in buildable_plants:
            if strike_price > plant.calculate_lcoe():
                viable_plants.append(plant)
        if len(viable_plants) != 0:
            return random.choice(viable_plants)

        
    def shutdown_unprofitable(self):
        '''
        shuts down unprofitable plants

        Not implemented
        '''
        pass
    def shutdown_old(self):
        '''
        shuts down plants that are too old

        '''
        pass

    def step(self, strike_price): 
        '''
        Each step the agent will chose whether to invest in new plants, or shut them down based on profitability
        '''
        plant_to_build = self.invest(strike_price, data.buildable_plants)
        if plant_to_build != None:
            self.plants.append(plant_to_build)
            print(f'Built {plant_to_build}')

