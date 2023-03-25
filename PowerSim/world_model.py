from typing import List
import numpy as np
import mesa


from electricity_company import ElecCo
import elec_market
import plants
from demand import DemandAgent
from capacity_factors import capacity_factors
import fuels
import plant_data
from plant_data import plant_generator

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
        buildable_plant_data,
        plant_cost_data,
        init_year: int = 2022,
        n_years: int = 30,
        n_days: int = 4,
        historical_strike_prices: List[float] = plant_data.historical_price_data,
        demand_variance: float = 500.0,
        data_folder = 'Data_out',
        downpayment_percent = 0.3,
        number_can_build = 5

        ):

        self.buildable_plant_data = buildable_plant_data
        self.plant_cost_data = plant_cost_data
        self.current_year = init_year
        self.n_years = n_years
        self.n_days = n_days
        self.power_plants = power_plants
        self.buildable_plants = []
        self.historical_strike_prices = historical_strike_prices
        self.demand_variance = demand_variance
        self.downpayment_percent = downpayment_percent
        
        self.years_since_start = 0
        self.average_yearly_prices = historical_strike_prices
        self.all_strike_prices = []
        self.all_plants_selected:List[List[List[plants.PowerPlant]]] = []
        self.average_strike_price = 40.0
        # mesa scheduler. Activates each agent once per step, in random order. In future, do simultaneous activation
        self.schedule = mesa.time.RandomActivation(self)
        # initialise demand agent
        self.demand = DemandAgent(1, self)
        self.hourly_demand = self.demand.hourly_demand_MW
        # initialise market
        self.market = elec_market.Market()
        # create data logger
        self.data_folder = data_folder
        # self.create_data_collector()
        self.plant_generator = plant_data.plant_generator()
        self.number_can_build = number_can_build

        self.initialise_gen_cos()

        self.elec_cos = self.get_elec_cos()
        

    def initialise_gen_cos(self):
        '''
        Using data from Data, initialise different gen_cos using the plants assossiciated with them. Linked to the dataframe which is bad
        '''
        for i, company_name in enumerate(set(plant_data.DUKES_plants_df.company_name)):
            co = ElecCo(i, self, company_name, [plant for plant in self.power_plants if plant.company is company_name])
            co.init_cash()
            co.lookforward_time = 10
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
        ''' Change in future to change based on year. Select 10 of each type'''
        buildable_plants = self.plant_generator.generate_buildable_plants_from_data(self.buildable_plant_data, self.plant_cost_data, self.number_can_build)
        return buildable_plants
        
    def get_demand(self) -> List:
        hourly_demand = self.demand.hourly_demand_MW
        return hourly_demand

    def world_day(self, random_day, hourly_demand:list, predict =False) -> list:
        '''Runs a day
        random_day: what day the capacity factors are picked for 
        '''
        day_strike_prices = []
        capacity_factors.set_daily_cfs(random_day)
        for hour, demand in enumerate(hourly_demand):
            ps = self.power_plants
            for p in ps:
                p.variable_costs_per_MWH = p.get_variable_costs()
            ps.sort(key = lambda x: x.variable_costs_per_MWH)
            price = self.market.fill_demand(demand, ps, hour, random_day, predict)
            day_strike_prices.append(price)

        if not predict:    
            self.all_strike_prices.append(day_strike_prices)
            self.average_strike_price = sum(day_strike_prices)/len(day_strike_prices)
            for elec_co in self.elec_cos:
                elec_co.get_paid(day_strike_prices)
        
        return day_strike_prices

    def world_step(self):
        '''
        advances model by a year. First runs the electricity for the number of days wanted,
        then steps the agents (they invest etc.)
        '''
            
        self.demand.step()
    
        for f in fuels.fuel_list:
            f.set_fuel_price()
        fuels.carbon_tax.set_carbon_tax(self.years_since_start)
        self.buildable_plants = self.get_buildable_plants()
        self.schedule.step()

        average_daily_prices = []

        #For each day, sorts all powerplants by their bid, then uses the market to fill the demand
        for _ in range(self.n_days):

            self.hourly_demand = self.get_demand()
        
            random_day = np.random.randint(0,capacity_factors.merra_data_days)
            self.world_day(random_day, self.hourly_demand)
            average_daily_prices.append(self.average_strike_price)



        self.average_yearly_prices.append(sum(average_daily_prices)/len(average_daily_prices))
        # self.datacollector.collect(self)
    
        self.current_year += 1
        self.years_since_start += 1

    def predicted_year_step(self, mean_demand_prediction:list, years_in_future: int):
        ''' Runs a predicted year. Returns list of random days selected in the year and all the prices found.
            demand_prediction: average predicted demands. In future, call the demand agent using the predicted averages. 
            years in future: how many years in future is the year that is used.
            '''

        random_day_list = []
        price_list = []

        '''demand prediction not used. Make it so that it is.'''
        hourly_demand = self.demand.hourly_demand_MW
        

        for elec_co in self.elec_cos:
            elec_co.set_whether_plants_operate(self.current_year + years_in_future)


        for _ in range(self.n_days):
            random_day = np.random.randint(0,capacity_factors.merra_data_days)
            random_day_list.append(random_day)
            prices = self.world_day(random_day, hourly_demand, predict=True)
            price_list.append(prices)

        '''Reset all the plants '''
        for elec_co in self.elec_cos:
            elec_co.set_whether_plants_operate(self.current_year)

        return random_day_list, price_list


    # def create_data_collector(self):
    #     ''' get this working'''
    #     self.datacollector = mesa.DataCollector(
    #         model_reporters={
    #             'daily_demand': lambda m: self.get_demand()
                
    #         }




    #     )
        

    # @staticmethod
    # def get_running_plants(model, )