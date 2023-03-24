
''' Gets the data for the plants'''


import random
import pandas as pd

import plants


historical_price_data = [70.0, 70.0, 70.0, 70.0, 70.0]



DUKES_plants_df = pd.read_csv(r'PowerSim/DUKES_5.11.csv')
DUKES_plants_df.dropna(axis=0,how='all',inplace=True)



plant_costs_df = pd.read_csv(r'PowerSim/plant_cost_data.csv')             
plant_costs_df.dropna(axis=0, how='all', inplace=True)

class plant_generator:
    def __init__(self):
        pass

    def generate_plant(self, a, cost_d: pd.DataFrame, is_operating, bc_error=0.1, fixed_cost_error = 0.1 , variable_error=0.1, operational_length_extension =0) -> plants.PowerPlant:
                
                bc_error = random.uniform(1-bc_error, 1+bc_error) 
                fixed_cost_error = random.uniform(1-fixed_cost_error, 1+fixed_cost_error) 
                variable_error = random.uniform(1-variable_error, 1+variable_error) 

                x = plants.PowerPlant(
                            name=a.plant_name,
                            technology=a.Technology,
                            company = a.company_name,
                            capacity_MW=a.installed_capacity_MW,
                            construction_start_date=a.year_commissioned,  
                            construction_end_date= a.year_commissioned,
                            operational_length_years= ((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['operating_lifetime'] + operational_length_extension), 
                            fuel_effeciency = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fuel_effeciency'],
                            build_costs = bc_error*((
                                        ((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['construction_cost_medium'] 
                                        + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['pre-development_cost_medium'])*a.installed_capacity_MW*1000 
                                        + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Infrastructure']*1000)),
                            construction_length= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['total_construction_period'],
                            fixed_costs_per_H = fixed_cost_error*(cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fixed_maintenance_costs']*a.installed_capacity_MW/8766
                                        + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Insurance']*a.installed_capacity_MW/8766.      
                                        + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['connection_costs']*a.installed_capacity_MW/8766,
                            variable_maintenance_per_MWh= variable_error*(cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['variable_maintenance'],
                            load_factor = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['load_factor'],
                            is_operating=is_operating
                        )
                return x


    def generate_plants_from_data(self, current_plant_database: pd.DataFrame, cost_d: pd.DataFrame, ol_extension):
        ''' Generate plants from database.'''
        A = [self.generate_plant(a, cost_d, True, operational_length_extension = ol_extension) for a in current_plant_database.itertuples()]

        return A

    def generate_buildable_plants_from_data(self, buildable_plant_database: pd.DataFrame, cost_d: pd.DataFrame, number):
        ''' Generate plants from database. gives number of each technology'''
        df = buildable_plant_database

        # define a lambda function to select 5 random rows for a group
        def select_random_rows(group):
            if len(group) >= number:
                return group.sample(n=5)
            else:
                return group

        # select 5 random rows for each unique value in column A
        bld_df = df.groupby('Technology', group_keys=True).apply(select_random_rows)



        A = [self.generate_plant(a, cost_d, False) for a in bld_df.itertuples()]
        return A






