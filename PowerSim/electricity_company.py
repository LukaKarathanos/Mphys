import copy
from typing import List
import numpy as np
import random
import mesa
import numpy_financial as npf

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

    def invest_better(self, predicted_prices: np.ndarray, buildable_plants: List[PowerPlant], downpayment_percent: float):
        ''' Uses a predicted electricity price per year to invest. Checks if company has enough money for the downpayment.
        picks highest npv per pound.
        '''
        viable_plants: List[PowerPlant] = []
        for plant in buildable_plants:
            if downpayment_percent*plant.build_costs < self.cash:
                plant.npv = ProfitCalculator.calculate_npv(plant, predicted_prices)
                if plant.npv > 0:
                    viable_plants.append(plant)
        if len(viable_plants) != 0:
            best_plant = max(viable_plants, key = lambda obj: obj.npv/obj.build_costs)
            return best_plant
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
        
    def init_cash(self):
        ''' 
        sets the initial cash each agent has, based on their current assets
        '''
        c = 0
        for plant in self.power_plants:
            y_to_operate: float = plant.operational_length_years + plant.construction_end_date - self.model.current_year
            plant_val = (y_to_operate/plant.operational_length_years)*plant.build_costs
            c += plant_val
        self.cash = c
    
    def get_paid(self, days_prices: list):
        '''Pay itself the net profit/loss from all the plants in the day. Assuming costs don't change during the day'''
        total_production = np.zeros(24)
        costs = 0
        for plant in self.power_plants: 
            if plant.is_operating: 
                production = np.array(plant.energy_supplied_per_hour[-24])
                total_production += production
                costs += np.sum(total_production*plant.variable_costs_per_MWH) + plant.fixed_costs_per_H*24       
        price = np.array(days_prices)
        revenue = np.sum(price*total_production)
        print(revenue)
        cashflow = (revenue - costs)*365/self.model.n_days + self.get_debt_payment()
        print(cashflow)
        
        self.cash += cashflow

    def get_debt_payment(self) -> float:
        ''' Gets the yearly debt payments'''
        debt = 0
        for plant in self.power_plants:
            if plant.is_operating:
                debt += plant.yearly_debt_payment
        for plant in self.build_queue:
            debt += plant.yearly_debt_payment
        return debt

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
        for _ in range(10):
            plant_to_build = self.invest_better(predicted_prices, buildable_plants, self.model.downpayment_percent)
            if plant_to_build is not None:     
                #adds plant to the build queue        
                plant_to_build.construction_start_date = self.model.current_year
                plant_to_build.construction_end_date = plant_to_build.construction_start_date + plant_to_build.construction_length
                plant_to_build.company = self.name
                plant_to_build.yearly_debt_payment = ProfitCalculator.calculate_yearly_debt(plant_to_build, self.model.downpayment_percent, plant_to_build.interest_rate)
                self.build_queue.append(plant_to_build)
                buildable_plants.remove(plant_to_build)
                self.cash -= plant_to_build.build_costs*self.model.downpayment_percent
                lcoe = plant_to_build.calculate_lcoe()
            else:
                break
        for plant in self.build_queue:
            if plant.construction_end_date == self.model.current_year:

                plant.is_operating = True
                self.power_plants.append(plant)

                self.build_queue.remove(plant)


        

