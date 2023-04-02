'''
agent that sets the demand. implement later.
Daily demand, varies alot - yearly demand remains constant.

just 1 day demand, per hour
Currently, list of average demands in MW

In future will simulate vehicle to grid to level out the demand.
'''

import numpy as np
import pandas as pd
import random
import datetime
from functools import lru_cache

import mesa

class DemandAgent(mesa.Agent):
    def __init__(self, unique_id, model: 'WorldModel', percent_increase):
        super().__init__(unique_id, model)
        self.yearly_increase = percent_increase
        self.demand_df = pd.read_csv(r'PowerSim/hist_demand_data.csv', parse_dates=['SETTLEMENT_DATE'])
        # Create a new column 'group' that groups every two row



        self.demand_list_normalised = self.demand_df['normalised_demand'].values
        
        self.average_demand = self.demand_df.loc[self.demand_df['SETTLEMENT_DATE'].dt.year == 2022, 'ND_and_renewables'].mean()



        '''change this in future. I have the historical demand stuff.'''
        self.historical_average_demand_list = [self.average_demand]*10

        
    def get_random_days_demand(self, day_of_year: int, av_demand: float):
        '''changes each time called'''
        day_str = self.get_day(day_of_year)
        demand = self.get_day_demand(day_str, av_demand)    
        return demand
     
    def get_day(self, day_of_year):
        '''returns random demand for a day in the year
        Imprecise for speed. sort tomorrow
        '''
        if day_of_year == 366:
            day_of_year = 365
        year = np.random.randint(2011,2022)
        year = random.randint(2011, 2022)
        date = (datetime.datetime(year, 1, 1) + datetime.timedelta(day_of_year - 1)).date()
        return date

        # y = np.random.randint(2011, 2022).
        # self.demand_df['SETTLEMENT_DATE']

    @lru_cache(maxsize=500)
    def get_day_demand(self, date, av_demand: float):
        ''' same each day called'''
        d = self.demand_df.loc[self.demand_df['SETTLEMENT_DATE'].dt.date == date, 'normalised_demand'].values
        demand = d*av_demand
        return demand.copy()
    
    def increasing_demand(self, increase = 1):
        self.average_demand = increase*self.average_demand

    def step(self):
        self.increasing_demand(self.yearly_increase)
        self.historical_average_demand_list.append(self.average_demand)






