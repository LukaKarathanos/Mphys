from typing import List
import numpy as np
import mesa


import data
from electricity_company import ElecCo
import elec_market
import plants
from demand import DemandAgent, hourly_demand_MW
import capacity_factors
import fuels

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
        power_plants: List[plants.PowerPlant],
        buildable_plants: List[plants.PowerPlant],
        init_year: int = 2022,
        n_years: int = 30,
        n_days: int = 4,
        initial_hourly_demand: List = hourly_demand_MW,    
        historical_strike_prices: List[float] = data.historical_price_data,
        demand_variance: float = 500.0,
        data_folder = 'Data_out'
        ):

        self.current_year = init_year
        self.n_years = n_years
        self.n_days = n_days
        self.initial_hourly_demand = initial_hourly_demand
        self.power_plants = power_plants
        self.buildable_plants = buildable_plants
        self.historical_strike_prices = historical_strike_prices
        self.demand_variance = demand_variance
        
        self.years_since_start = 0
        self.average_yearly_prices = historical_strike_prices
        self.all_strike_prices = []
        self.all_plants_selected:List[List[List[plants.PowerPlant]]] = []
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
        # self.create_data_collector()

    def initialise_gen_cos(self):
        '''
        Using data from Data, initialise different gen_cos using the plants assossiciated with them. Linked to the dataframe which is bad
        '''
        for i, company_name in enumerate(set(data.DUKES_plants_df.company_name)):
            co = ElecCo(i, self, company_name, [plant for plant in self.power_plants if plant.company is company_name], cash = 5_000_000_000)
            self.schedule.add(co)

    def get_elec_cos(self) -> List[ElecCo]:
        elec_cos = [elec_co for elec_co in self.schedule.agents if isinstance(elec_co, ElecCo)]
        return elec_cos

    def get_plants(self) -> List[plants.PowerPlant]:
        elec_cos = self.get_elec_cos()
        plant_list = []
        for elec_co in elec_cos:
            plant_list.append(elec_co.power_plants)
        plant_list = list(np.concatenate(plant_list).flat)
        return plant_list 
        
    def get_buildable_plants(self) -> List[plants.PowerPlant]:
        ''' Change in future to change based on year.'''
        return self.buildable_plants
        
    def get_demand(self) -> List:
        hourly_demand = self.demand.get_daily_demand()
        return hourly_demand

    def world_step(self):
        '''
        advances model by a year. First runs the electricity for the number of days wanted,
        then steps the agents (they invest etc. )
        '''
            
        self.demand.step()
        
        for f in fuels.fuel_list:
            f.set_fuel_price()

        self.schedule.step()

        elec_cos = self.get_elec_cos()
        average_daily_prices = []

        #For each day, sorts all powerplants by their bid, then uses the market to fill the demand
        for i in range(self.n_days):
            
            random_day = np.random.randint(0,capacity_factors.merra_data_days)
            day_strike_prices = []
            day_plants_selected:List[List[plants.PowerPlant]] = []
            # daily demand varies 
            self.demand.vary_daily_demand(self.demand_variance)
            self.hourly_demand = self.get_demand()

            for hour, demand in enumerate(self.hourly_demand):
                ps = self.get_plants()
                for p in ps:
                    p.variable_costs_per_MWH = p.get_variable_costs()
                ps.sort(key = lambda x: x.variable_costs_per_MWH)
                price, plants_selected = self.market.fill_demand(demand, ps, hour, random_day)
                day_strike_prices.append(price)
                day_plants_selected.append(plants_selected)
            self.all_strike_prices.append(day_strike_prices)
            self.all_plants_selected.append(day_plants_selected)
            self.average_strike_price = sum(day_strike_prices)/len(day_strike_prices)
            average_daily_prices.append(self.average_strike_price)
        self.average_yearly_prices.append(sum(average_daily_prices)/len(average_daily_prices))
        
        # self.datacollector.collect(self)
        

        self.current_year += 1


    # def create_data_collector(self):
    #     ''' get this working'''
    #     self.datacollector = mesa.DataCollector(
    #         model_reporters={
    #             'daily_demand': lambda m: self.get_demand()
                
    #         }




    #     )
        

    # @staticmethod
    # def get_running_plants(model, )