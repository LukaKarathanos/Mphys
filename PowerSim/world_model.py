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
from storage_company import StorageCo

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
        storage_plants: List[plants.StoragePlant],
        buildable_plant_data,
        plant_cost_data,
        init_year: int = 2022,
        n_years: int = 30,
        n_days: int = 4,
        historical_strike_prices: List[float] = plant_data.historical_price_data,
        demand_variance: float = 500.0,
        data_folder = 'Data_out',
        downpayment_percent = 0.3,
        number_can_build = 50,
        storage_co_n = 10,
        yearly_storage_increase = 1000,
        demand_increase_factor = 1.01
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
        self.storage_plants = storage_plants    
        self.yearly_storage_increase_per_company = yearly_storage_increase/storage_co_n

        self.years_since_start = 0
        self.average_yearly_prices = historical_strike_prices
        self.all_strike_prices = []
        self.all_plants_selected:List[List[List[plants.PowerPlant]]] = []
        self.average_strike_price = 40.0
        # mesa scheduler. Activates each agent once per step, in random order. In future, do simultaneous activation
        self.schedule = mesa.time.RandomActivation(self)
        # initialise demand agent
        self.demand = DemandAgent(1, self, demand_increase_factor)
        # initialise market
        self.market = elec_market.Market()
        # create data logger
        self.data_folder = data_folder
        # self.create_data_collector()
        self.plant_generator = plant_data.plant_generator()
        self.number_can_build = number_can_build

        self.initialise_gen_cos()
        self.initialise_storage_cos(range(storage_co_n))

        self.elec_cos = self.get_elec_cos()
        self.storage_cos = self.get_storage_cos()
        

    def initialise_gen_cos(self):
        '''
        Using data from Data, initialise different gen_cos using the plants assossiciated with them. Linked to the dataframe which is bad
        '''
        for i, company_name in enumerate(set(plant_data.DUKES_plants_df.company_name)):
            co = ElecCo(i, self, company_name, [plant for plant in self.power_plants if plant.company_name is company_name])
            for plant in co.power_plants:
                plant.company = co
            co.init_cash()
            co.lookforward_time = 10
            self.schedule.add(co)
            
    def initialise_storage_cos(self, names):
        for company_name in names:
            co = StorageCo(f'store co {company_name}', self, company_name, [plant for plant in self.storage_plants if plant.company_name is company_name])
            for plant in co.storage_plants:
                plant.company = co
            self.schedule.add(co)

    def get_elec_cos(self) -> List[ElecCo]:
        elec_cos = [elec_co for elec_co in self.schedule.agents if isinstance(elec_co, ElecCo)]
        return elec_cos
    
    def get_storage_cos(self):
        store_cos = [store_co for store_co in self.schedule.agents if isinstance(store_co, StorageCo)]
        return store_cos

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
        
    def get_demand(self) -> np.ndarray:
        hourly_demand = self.demand.hourly_demand_MW
        return hourly_demand

    def world_day(self, random_day, hourly_demand:np.ndarray, predict =False) -> list:
        '''Runs a day
        random_day: what day the capacity factors are picked for 
        '''


        '''Storage stuff'''
        stored_amount = np.zeros(24)
        # np.random.shuffle(self.storage_cos)

        for storage_co in self.storage_cos:
            stored_amount += storage_co.day_step(random_day, hourly_demand, stored_amount, predict)

        hourly_demand = hourly_demand + stored_amount
        day_strike_prices = self.day_demand_fill(random_day, hourly_demand, predict)
        return day_strike_prices

    def day_demand_fill(self, random_day, hourly_demand, predict = False):

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
        # self.buildable_plants = self.get_buildable_plants()
        
        for storage_plant in self.storage_plants:
            storage_plant.set_storage_amount(self.yearly_storage_increase_per_company*(self.years_since_start+1))
            
        self.schedule.step()

        average_daily_prices = []

        random_day_list, rd_in_years_list = self.get_random_days(self.n_days)

        #For each day, sorts all powerplants by their bid, then uses the market to fill the demand
        for i in range(self.n_days):
            demand = self.demand.get_random_days_demand(rd_in_years_list[i],self.demand.average_demand)
            self.world_day(random_day_list[i], demand, predict=False)
            average_daily_prices.append(self.average_strike_price)

        self.average_yearly_prices.append(sum(average_daily_prices)/len(average_daily_prices))
    
        self.current_year += 1
        self.years_since_start += 1

    def predicted_year_step(self, mean_demand_prediction:float, years_in_future: int, n_days):
        ''' Runs a predicted year. Returns list of random days selected in the year and all the prices found.
            demand_prediction: average predicted demands. In future, call the demand agent using the predicted averages. 
            years in future: how many years in future is the year that is used.
            '''

        price_list = []

        for elec_co in self.elec_cos:
            elec_co.set_whether_plants_operate(self.current_year + years_in_future)

        '''random days done by splitting years up, to account for seasonality'''
        random_day_list, rd_in_years_list = self.get_random_days(n_days)

        for i in range(n_days):
            demand = self.demand.get_random_days_demand(rd_in_years_list[i],mean_demand_prediction)
            prices = self.world_day(random_day_list[i], demand, predict=True)
            price_list.append(prices)

        '''Reset all the plants '''
        for elec_co in self.elec_cos:
            elec_co.set_whether_plants_operate(self.current_year)

        return random_day_list, price_list

    def get_random_days(self,n_days):
        year_fraction = 365.25/n_days
        rd_list = []
        rd_in_y_list = []
        for n in range(n_days):
            random_year = np.random.randint(0, 40)
            random_day_in_year = np.random.randint(int(n*year_fraction), int((n+1)*year_fraction))
            random_day = int(random_year*365.25+random_day_in_year)
            rd_list.append(random_day)
            rd_in_y_list.append(random_day_in_year)
        return rd_list, rd_in_y_list