import copy
from typing import List
import numpy as np
import random
import mesa
import numpy_financial as npf

from predictor import Forecast
from plants import PowerPlant
from investing import ProfitCalculator
import fuels

if __name__ == '__main__':
    from world_model import WorldModel

class ElecCo(mesa.Agent):
    '''
    Agent. Starts with powerplants and money. Using predictions of future elec. prices and fuel costs, will choose if and what
    to invest in -> not implemented. 
    Currently just choses whether to invest or not.  
    '''
    def __init__(self, unique_id, model, name: str, power_plants:List[PowerPlant], cash: float = 0, lookforward_time = 20, lookback_time = 5):
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
        self.lookforward_time = lookforward_time
        self.lookback_time = lookback_time
        self.bid_increase_factor = np.random.uniform(1,1.25)
        self.n_days = 6
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
            return [best_plant]
        else:
            return None
        
    def shutdown_unprofitable(self):
        '''
        shuts down unprofitable plants

        Not implemented
        '''
        pass

    def set_whether_plants_operate(self, current_year):
        '''
        checks whether plant can run in the current year. Else sets plant running to false.
                '''
        for plant in self.power_plants:
            if (plant.operational_length_years + plant.construction_end_date) < current_year:
                plant.is_operating = False
            elif plant.construction_end_date > current_year:
                plant.is_operating = False
            else:
                plant.is_operating = True

    def init_cash(self):
        ''' 
        sets the initial cash each agent has, based on their current assets
        '''
        c = 0
        for plant in self.power_plants:
            y_to_operate: float = plant.operational_length_years + plant.construction_end_date - self.model.current_year
            plant_val = (y_to_operate/plant.operational_length_years)*plant.build_costs
            c += plant_val
        self.cash = c*0.5
    
    def get_paid(self, days_prices: list):
        '''Pay itself the net profit/loss from all the plants in the day. Assuming costs don't change during the day'''
        total_production = np.zeros(24)
        costs = 0
        for plant in self.power_plants: 
            if plant.is_operating: 
                production = np.array(plant.energy_supplied_per_hour[-24:])
                total_production = production + total_production
                costs += np.sum(production*plant.variable_costs_per_MWH) + plant.fixed_costs_per_H*24       
        price = np.array(days_prices)
        revenue = np.sum(price*total_production)
        # print(revenue)
        cashflow = (revenue - costs)*365.25/self.model.n_days
        self.cash += cashflow

    def pay_debts(self):
        self.cash += self.get_debt_payment()

    def get_debt_payment(self) -> float:
        ''' Gets the yearly debt payments'''
        debt = 0
        for plant in self.power_plants:
            if plant.is_operating:
                debt += plant.yearly_debt_payment
        # for plant in self.build_queue:
        #     debt += plant.yearly_debt_payment
        return debt

    def step(self): 
        '''
        Each step the agent will chose whether to invest in new plants, or shut them down based on profitability
        runs investement 5 times 
        Checks whether there are profitable plants, then choses to build one. The plant is then appended to the build queue.
        predict: if is part of prediction or not 
        '''
        self.set_whether_plants_operate(self.model.current_year)
        self.pay_debts()
        self.bid_increase_factor = np.random.uniform(1,1.25)
        buildable_plants = self.model.get_buildable_plants()

        plants_to_build = self.invest_proper(buildable_plants, self.model.downpayment_percent)

        if plants_to_build is not None:     
            #adds plant to the build queue
            for plant in plants_to_build:
                if self.cash > plant.build_costs*self.model.downpayment_percent:        
                    plant.construction_start_date = self.model.current_year
                    plant.construction_end_date = plant.construction_start_date + plant.construction_length
                    plant.company = self
                    plant.yearly_debt_payment = ProfitCalculator.calculate_yearly_debt(plant, self.model.downpayment_percent, plant.interest_rate)

                    # add plants to the lists of plants they are part of. Plants are never removed. 
                    self.build_queue.append(plant)
                    self.power_plants.append(plant)
                    self.model.power_plants.append(plant)
                    buildable_plants.remove(plant)
                    self.cash -= plant.build_costs*self.model.downpayment_percent
                else:
                    break

        for plant in self.build_queue:

            if plant.construction_end_date == self.model.current_year:

                plant.is_operating = True

                self.build_queue.remove(plant)
    
    def invest_proper(self, buildable_plants:List[PowerPlant], downpayment_percent):
        ''' Runs the predictor, then runs model n years in advance. 
        For buildable plants, find out their cashflow using this.

        Build viable plants until money runs out or 5 plants built. 
        '''
        
        viable_plants: List[PowerPlant] = []
        predicted_average_demand: list = Forecast.historical(self.model.demand.historical_average_demand_list, self.lookback_time, self.lookforward_time)[-1]
        
        '''predict fuel price'''
        for fuel in fuels.fuel_list:
            predicted_fuel_price = Forecast.historical(fuel.fuel_price_history, self.lookback_time, self.lookforward_time)[-1]
            fuel.fuel_price = predicted_fuel_price
        
        year_since_start = self.model.years_since_start + self.lookforward_time

        '''Carbon tax increase is known.'''
        fuels.carbon_tax.set_carbon_tax(year_since_start)


        random_day_list, price_list = self.model.predicted_year_step(predicted_average_demand, self.lookforward_time, self.n_days)

        ''''set capacity factor '''

        '''find each plants cashflow'''
        for plant in buildable_plants:
            if downpayment_percent*plant.build_costs < self.cash:
                cashflow = 0.0
                plant.variable_costs_per_MWH = plant.get_variable_costs()

                for i, day_prices in enumerate(price_list):
                    day_prices = np.array(day_prices)
                    a = day_prices > plant.variable_costs_per_MWH
                    pot_production = plant.get_capacity_factor(plant.technology, random_day_list[i])*plant.capacity_MW
                    pot_revenue = pot_production*day_prices
                    if a.shape != pot_revenue.shape:
                        raise ValueError("Arrays must have the same shape")

                    total_revenue = pot_revenue[a].sum()
                    total_costs = plant.fixed_costs_per_H*24 + pot_production[a].sum()*plant.variable_costs_per_MWH

                    cash = total_revenue - total_costs
                    cashflow += cash
                
                cashflow = cashflow*365.25/self.model.n_days
                plant.npv = ProfitCalculator.calculate_npv_proper(plant, cashflow)
                if plant.npv > 0:
                    viable_plants.append(plant)

        '''reset fuel price'''
        for fuel in fuels.fuel_list:
            fuel.fuel_price = fuel.fuel_price_history[-1]
        

       
        if len(viable_plants) != 0:
            best_plants = sorted(viable_plants, key = lambda obj: obj.npv/obj.build_costs, reverse = True)
            return best_plants
        
        else:
            return None

