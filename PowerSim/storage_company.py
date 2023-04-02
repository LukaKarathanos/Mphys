from dataclasses import dataclass, field
from typing import List
import mesa
import numpy as np
import multiprocessing
import time 
from functools import partial 
from predictor import Forecast
from plants import StoragePlant

class StorageCo(mesa.Agent):
    ''' Storage agent. Owns storage capacity'''
    def __init__(self, unique_id, model, name: str, storage_plants:List[StoragePlant], cash: float = 0, lookforward_days = 1, lookback_time = 5):
        '''
        electricity company definition
        name: unique name 
        initial_plants: power plants that it is initialised with
        cash: amount of free cash it starts with. Used to pay downpayments for the powerplants

        '''
        super().__init__(unique_id, model)
        self.name = name
        self.storage_plants = storage_plants
        self.cash = cash
        self.build_queue:List[StoragePlant] = []
        self.model = model
        self.lookforward_days = lookforward_days
        self.lookback_time = lookback_time


    def day_step(self, random_day, demand, storage_amounts: np.ndarray, predict=False):
        '''Make prediction. Set storage production for the day.  Returns the amount of electricity all the plants of the company store/produce.'''
        ts = time.time()
        act_demand = demand - storage_amounts
        predicted_prices = self.model.day_demand_fill(random_day, act_demand, predict=True)

        if len(self.model.all_strike_prices)>=6:
            average_price = list(self.av_day_strike_prices(self.model.all_strike_prices))*self.lookforward_days
        else:
            average_price = predicted_prices*self.lookforward_days

        predicted_prices.extend(average_price)

        total_stored = np.zeros(24)

        # inputs = self.storage_plants

        # # Create a partial function with the fixed inputs
        # partial_process_input = partial(self.please_work, predict=predict, predicted_prices = predicted_prices)

        # # Create a pool of worker processes
        # pool = multiprocessing.Pool()

        # # Map the variable inputs to the partial function using the pool of processes
        # results = pool.map(partial_process_input, inputs)

        # # Close the pool of worker processes
        # pool.close()
        # pool.join()

        # total_stored = np.sum(results, axis=0)

        for plant in self.storage_plants:
            prod = plant.get_days_production(predicted_prices)
            if not predict:
                plant.energy_supplied_per_hour.extend(prod)
            total_stored += -np.array(prod)

        ts -= time.time()
        # print(ts)
        return total_stored
    
    def av_day_strike_prices(self,all_prices:List[List[float]],days=6):
        '''gets average hourly strike prices for one day'''
        ps = np.array(all_prices[-days:])
        av_ps = np.mean(ps, 0)
        return av_ps

    def please_work(self, plant, predict, predicted_prices):
        prod = plant.get_days_production(predicted_prices)
        if not predict:
            plant.energy_supplied_per_hour.extend(prod)
        return np.array(prod)
    
    # def step(self):
    #     '''Sets the capacities of the storage plants'''
    #     for plant in self.storage_plants:
    #         self.model.
    #         plant.set_data()