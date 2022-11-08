import numpy as np
import random
import mesa



class ElecCo(mesa.Agent):
    def __init__(self, name, initial_plants=None, cash = ):
        '''
        electricity company definition
        name: unique name 
        initial_plants: power plants that it is initialised with
        cash: amount of money it starts with
        '''
        pass

    def invest(self):
        '''
        If have free money, find best power plants to invest in
        '''
        pass
    def shutdown_unprofitable(self):
        '''
        shuts down unprofitable plants
        '''
        pass
    def shutdown_old(self):
        '''
        shuts down plants that are too old
        '''
        pass
    def 