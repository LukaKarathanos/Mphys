import numpy as np
from electricity_company import ElecCo
import data
import mesa
import elec_market
import plants
from demand import DemandAgent, hourly_demand_MW

import itertools

class WorldModel(mesa.Model):
    '''
    Defines the model world that is being used. expand further -> put the run function in here to make more tidy
    Sets the initial parameters
    defines step function

    Will create the instances of the elec companies and demand agents.
    Contains the world data which the other functions and classes use
    '''
    def __init__(
        self, 
        n_gen_cos: int,
        power_plants: list[plants.PowerPlant],
        init_year: int = 2022,
        n_years: int = 30,
        n_days: int = 4,
        initial_hourly_demand: list = hourly_demand_MW,    
        historical_strike_prices: list[float] = data.historical_price_data,
        demand_variance: float = 500.0,
        data_folder = 'Data_out'
        ):

        self.current_year = init_year
        self.n_years = n_years
        self.n_days = n_days
        self.initial_hourly_demand = initial_hourly_demand
        self.n_gen_cos = n_gen_cos
        self.power_plants = power_plants
        self.historical_strike_prices = historical_strike_prices
        self.demand_variance = demand_variance
        
        self.years_since_start = 0
        self.average_yearly_prices = historical_strike_prices
        self.all_strike_prices = []
        self.all_plants_selected:list[list[list[plants.PowerPlant]]] = []
        self.average_strike_price = 40.0
        # mesa scheduler. Activates each agent once per step, in random order. In future, do simultaneous activation
        self.schedule = mesa.time.RandomActivation(self)
        # initialise demand agent
        self.demand = DemandAgent(1, self, initial_hourly_demand)
        self.hourly_demand = self.demand.hourly_demand_MW
        # initialise market
        self.market = elec_market.Market()
        # create data logger
        self.data_folder = data_folder
        self.create_data_collector()

    def initialise_gen_cos(self):
        '''
        Using data from Data, initialise different gen_cos using the plants assossiciated with them. Linked to the dataframe which is bad
        '''
        for i, company_name in enumerate(set(data.DUKES_plants_df.company_name)):
            co = ElecCo(i, self, company_name, [plant for plant in self.power_plants if plant.company is company_name], cash = 5_000_000_000)
            self.schedule.add(co)

    def get_elec_cos(self) -> list[ElecCo]:
        elec_cos = [elec_co for elec_co in self.schedule.agents if isinstance(elec_co, ElecCo)]
        return elec_cos

    def get_demand(self) -> list:
        hourly_demand = self.demand.get_daily_demand()
        return hourly_demand

    def world_step(self):
        '''
        advances model by a year. First runs the electricity for the number of days wanted,
        then steps the agents (they invest etc. )
        '''
        elec_cos = self.get_elec_cos()
        average_daily_prices = []

        #For each day, sorts all powerplants by their bid, then uses the market to fill the demand
        for i in range(self.n_days):
            day_strike_prices = []
            day_plants_selected:list[list[plants.PowerPlant]] = []
            # daily demand varies 
            self.demand.vary_daily_demand(self.demand_variance)
            self.hourly_demand = self.get_demand()

            for n, demand in enumerate(self.hourly_demand):
                ps = [elec_co.power_plants for elec_co in elec_cos]
                ps = list(itertools.chain.from_iterable(ps))
                for p in ps:
                    p.variable_costs_per_MWH = p.get_variable_costs()
                ps.sort(key = lambda x: x.variable_costs_per_MWH)
                price, plants_selected = self.market.fill_demand(demand, ps)
                day_strike_prices.append(price)
                day_plants_selected.append(plants_selected)
            self.all_strike_prices.append(day_strike_prices)
            self.all_plants_selected.append(day_plants_selected)
            self.average_strike_price = sum(day_strike_prices)/len(day_strike_prices)
            average_daily_prices.append(self.average_strike_price)
        self.average_yearly_prices.append(sum(average_daily_prices)/len(average_daily_prices))
        
        # self.datacollector.collect(self)
        
        self.demand.step()
        self.schedule.step()
        self.current_year += 1


    def create_data_collector(self):
        ''' get this working'''
        self.datacollector = mesa.DataCollector(
            model_reporters={
                'daily_demand': lambda m: self.get_demand()
                
            }




        )
        

    # @staticmethod
    # def get_running_plants(model, )