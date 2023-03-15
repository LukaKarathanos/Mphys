'''
agent that sets the demand. implement later.
Daily demand, varies alot - yearly demand remains constant.

just 1 day demand, per hour
Currently, list of average demands in MW

In future will simulate vehicle to grid to level out the demand.
'''
from typing import List

import mesa
import numpy as np
import pandas as pd

#from world_model import WorldModel



# hourly_demand_MW = [20000, 20000, 20000, 20000,
#         20000, 20000, 20000, 20000,
#         20000, 20000, 20000, 20000,
#         20000, 20000, 20000, 20000,
#         20000, 20000, 20000, 20000,
#         20000, 20000, 20000, 20000]



# hourly_demand_MW = [15000, 30000, 20000]

class DemandAgent(mesa.Agent):
    def __init__(self, unique_id, model: 'WorldModel'):
        super().__init__(unique_id, model)
        
        df = pd.read_csv(r'PowerSim/archive/noNaN_2022_demand.csv')
        # Create a new column 'group' that groups every two rows
        df['group'] = (df.index // 2)
        #national demand plus embedded wind and solar
        df['true_demand'] = df['nd'] + df['embedded_wind_generation'] + df['embedded_solar_generation']
        # Use groupby to group the DataFrame by 'group', then compute the mean
        df24 = df.groupby('group').mean()
        df24['settlement_period'] = (df24['settlement_period'] + 0.5)/2
        grouped_df = df24.groupby('settlement_period').agg(['mean', 'median', 'std'])

        self.demand_df = grouped_df

        self.hourly_demand_MW = self.demand_df['nd']['mean'].values

        #print(grouped_df)

        

    def increasing_demand(self, increase = 1):
        self.hourly_demand_MW = increase*self.hourly_demand_MW

    def vary_daily_demand(self,variance):
        '''Demand varies by day'''
        #d = np.random.normal(self.hourly_demand_MW, variance)
        d = self.hourly_demand_MW
        self.daily_demand = d
    
    def step(self):
        self.increasing_demand()






