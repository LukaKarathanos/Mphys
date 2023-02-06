'''
agent that sets the demand. implement later.
Daily demand, varies alot - yearly demand remains constant.

just 1 day demand, per hour
Currently, list of average demands in MW

In future will simulate vehicle to grid to level out the demand.
'''
import mesa
import numpy as np

#from world_model import WorldModel

hourly_demand_MW = [25000, 20000, 20000, 20000,
        20000, 25000, 25000, 30000,
        30000, 40000, 40000, 40000,
        40000, 40000, 40000, 40000,
        40000, 40000, 40000, 40000,
        40000, 35000, 30000, 25000]


# hourly_demand_MW = [15000, 30000, 20000]

class DemandAgent(mesa.Agent):
    def __init__(self, unique_id, model: 'WorldModel', hourly_demand_MW: list[float]):
        super().__init__(unique_id, model)
        self.hourly_demand_MW = np.array(hourly_demand_MW)

    def increasing_demand(self, increase = 1.01):
        self.hourly_demand_MW = increase*self.hourly_demand_MW

    def vary_daily_demand(self,variance):
        '''Demand varies by day'''
        #d = np.random.normal(self.hourly_demand_MW, variance)
        d = self.hourly_demand_MW
        self.daily_demand = d
    
    def get_daily_demand(self):
        return self.daily_demand

    def step(self):
        self.increasing_demand()






