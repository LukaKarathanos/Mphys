'''
Module containing the market which sets the strike price.
Need a way to predict the cost for the day ahead. Demand agent can use this to level out demand
(vehicle to grid, demand side flexible tariffs)
Also need long term prediction, which elecco agents can use to decide whether to invest.  
'''

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

    def fill_demand(self, demand:float, plants_to_fill: list[plants.PowerPlant]) -> tuple[float, list]:
        '''
        returns the strike price and the list of powerplants that were selected.
        plants must be ordered.
        '''
        total_bought = 0
        strike_price = 0
        bids = []
        plants_selected = []
        for plant in plants_to_fill:
            bid_price = plant.variable_costs_per_MWH
            gen_amount = plant.load_factor*plant.capacity_MW
            if total_bought + gen_amount >= demand:
                #fractional bid
                total_bought += demand - total_bought
                bids.append(bid_price)
                break
            else:
                bids.append(bid_price)
                total_bought += gen_amount
            strike_price = bids[-1]
            plants_selected += [plant]

        return strike_price, plants_selected


