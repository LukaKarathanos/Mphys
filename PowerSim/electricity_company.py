import copy
from typing import List
import numpy as np
import random
import mesa


#import world_model
from predictor import ForecastSpotPrice
from plants import PowerPlant
from investing import ProfitCalculator

class ElecCo(mesa.Agent):
    '''
    Agent. Starts with powerplants and money. Using predictions of future elec. prices and fuel costs, will choose if and what
    to invest in -> not implemented. 
    Currently just choses whether to invest or not.  
    '''
    def __init__(self, unique_id, model, name: str, power_plants:List[PowerPlant], cash: float = 0):
        '''
        electricity company definition
        name: unique name 
        initial_plants: power plants that it is initialised with
        cash: amount of free cash it starts with. Used to pay downpayments for the powerplants

        '''
        super().__init__(unique_id, model)
        self.name = name
        self.power_plants = power_plants
        self.cash = cash
        self.build_queue:List[PowerPlant] = []
        self.model = model

    def invest_better(self, predicted_prices: np.ndarray, buildable_plants: List[PowerPlant]):
        ''' Uses a predicted electricity price per year to invest. '''
        viable_plants: List[PowerPlant] = []
        for plant in buildable_plants:
            npv = ProfitCalculator.calculate_npv(plant, predicted_prices)
            if npv > 0:
                viable_plants.append(plant)
        if len(viable_plants) != 0:
            return random.choice(viable_plants)
        else:
            return None

    def invest_primitive(self, strike_price: float, buildable_plants: List[PowerPlant]):
        '''
        If plant lcoe is lower than strike price, build it.
        In future, more checks whether it would be profitable and choose the best one to build.
                
        '''
        viable_plants: List[PowerPlant] = []
        for plant in buildable_plants:
            if strike_price > plant.calculate_lcoe():
                viable_plants.append(plant)
        if len(viable_plants) != 0:
            return random.choice(viable_plants)
        else:
            return None

        
    def shutdown_unprofitable(self):
        '''
        shuts down unprofitable plants

        Not implemented
        '''
        pass
    def shutdown_old(self, current_year):
        '''
        shuts down plants that are too old
        '''
        for plant in self.power_plants:
            if (plant.operational_length_years + plant.construction_end_date) < current_year:
                plant.is_operating = False
        

    def step(self): 
        '''
        Each step the agent will chose whether to invest in new plants, or shut them down based on profitability
        runs investement 5 times 
        Checks whether there are profitable plants, then choses to build one. The plant is then appended to the build queue. 
        '''
        strike_price = self.model.average_strike_price
        self.shutdown_old(self.model.current_year)
        predicted_prices = ForecastSpotPrice.historical(self.model.average_yearly_prices)
        buildable_plants = self.model.buildable_plants
        for _ in range(3):
            plant_to_build = self.invest_better(predicted_prices, buildable_plants)
            if plant_to_build is not None:     
                #adds plant to the build queue        
                plant_to_build = copy.copy(plant_to_build)
                plant_to_build.construction_start_date = self.model.current_year
                plant_to_build.construction_end_date = plant_to_build.construction_start_date + plant_to_build.construction_length
                plant_to_build.company = self.name
                self.build_queue.append(plant_to_build)
                lcoe = plant_to_build.calculate_lcoe()
        for plant in self.build_queue:
            if plant.construction_end_date == self.model.current_year:

                plant.is_operating = True
                self.power_plants.append(plant)

                self.build_queue.remove(plant)


        

