'''
Module containing the market which sets the strike price.
Need a way to predict the cost for the day ahead. Demand agent can use this to level out demand
(vehicle to grid, demand side flexible tariffs)
Also need long term prediction, which elecco agents can use to decide whether to invest.  
'''
from typing import List, Tuple
import plants 




class Market:

    '''
    gets srmc bids from all power plants. orders by price, then picks until demand is filled
    This sets the strike price, which is what the companies are payed.
    '''
    def __init__(self):
        pass
    # def sort_plant_bids(self, plants:list) -> list:
    #     return plants.sort()

    def fill_demand(self, demand:float, plants_to_fill: List[plants.PowerPlant], hour: int, day: int, predict = False) -> float:
        '''
        returns the strike price.
        plants must be ordered. sets the amount the plants have supplied if predict is false. 
        '''
        filled = False
        bid_percent_increase = 1.2
        total_bought = 0
        strike_price = 0
        bids = []
        for plant in plants_to_fill:
            if plant.is_operating:
                bid_price = plant.variable_costs_per_MWH*bid_percent_increase
                gen_amount:float = plant.get_capacity_factor(plant.technology)[hour]*plant.capacity_MW
                if filled: 
                    if not predict:
                        plant.energy_supplied_per_hour.append(0)
                elif total_bought + gen_amount >= demand:
                    #fractional bid
                    c = demand - total_bought
                    total_bought += c
                    if not predict:    
                        plant.energy_supplied_per_hour.append(c)

                    bids.append(bid_price)
                    filled = True

                else:
                    bids.append(bid_price)
                    total_bought += gen_amount
                    if not predict:
                        plant.energy_supplied_per_hour.append(gen_amount)
                strike_price = bids[-1]
            elif not predict:
                plant.energy_supplied_per_hour.append(0)
        return strike_price


