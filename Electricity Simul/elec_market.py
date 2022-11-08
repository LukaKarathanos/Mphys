import numpy as np
import plants
from typing import Type




class Market:

    '''
    gets srmc bids from all power plants. orders by price, then picks until demand is filled
    This sets the strike price, which is what the companies are payed. 
    '''
    def __init__(self):
        pass
    # def sort_plant_bids(self, plants:list) -> list:
    #     return plants.sort()
    
    def fill_demand(self, demand:float, plants: list[Type[plants.PowerPlant]]) -> tuple[float, list]:
        '''
        returns the strike price and the list of powerplants that were selected. Cannot do partional bids, so will buy more
        than demand -> implement later 
        '''
        total_bought = 0
        bids = [] 
        plants_selected = []
        for plant in plants:
            if total_bought <= demand:
                bid = plant.variable_costs_per_MWH
                bids.append(bid)
                total_bought += bid*plant.capacity_MW
                strike_price = bids[-1]
                plants_selected += [plant]
            else:
                break
        return strike_price, plants_selected


            
                    
