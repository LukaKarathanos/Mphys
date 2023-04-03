
''' Gets the data for the plants'''


import random
import pandas as pd

import plants


historical_price_data = [70.0, 70.0, 70.0, 70.0, 70.0, ]



DUKES_plants_df = pd.read_csv(r'PowerSim/DUKES_5.11.csv')
DUKES_plants_df.dropna(axis=0,how='all',inplace=True)



plant_costs_df = pd.read_csv(r'PowerSim/plant_cost_data.csv')             
plant_costs_df.dropna(axis=0, how='all', inplace=True)

storage_data_df = pd.read_csv(r'PowerSim/storage_data.csv') 

class plant_generator:
    def __init__(self):
        pass
    def generate_plant(self, a, cost_d: pd.DataFrame, is_operating, bc_error=0.15, fixed_cost_error = 0.1 , variable_error=0.20, operational_length_extension =0) -> plants.PowerPlant:
                
                bc_error = random.uniform(1-bc_error, 1+bc_error) 
                fixed_cost_error = random.uniform(1-fixed_cost_error, 1+fixed_cost_error) 
                variable_error = random.uniform(1-variable_error, 1+variable_error) 

                cost_d_row = cost_d[cost_d['Technology'] == a.Technology].iloc[0].to_dict()
                installed_capacity = a.installed_capacity_MW*cost_d_row['capacity_increase_factor']
                x = plants.PowerPlant(
                            name=a.plant_name,
                            technology=a.Technology,
                            company_name = a.company_name,
                            capacity_MW=installed_capacity,
                            construction_start_date=a.year_commissioned,  
                            construction_end_date= a.year_commissioned,
                            operational_length_years= (cost_d_row['operating_lifetime'] + operational_length_extension), 
                            fuel_effeciency = cost_d_row['fuel_effeciency'],
                            build_costs = bc_error*((
                                        (cost_d_row['construction_cost_medium'] 
                                        + cost_d_row['pre-development_cost_medium'])*installed_capacity*1000 
                                        + cost_d_row['infrastructure_per_kW']*1000)),
                            construction_length= cost_d_row['total_construction_period'],
                            fixed_costs_per_H = fixed_cost_error*cost_d_row['fixed_maintenance_costs']*installed_capacity/8766
                                        + cost_d_row['Insurance']*installed_capacity/8766.      
                                        + cost_d_row['connection_costs']*installed_capacity/8766,
                            variable_maintenance_per_MWh= variable_error*cost_d_row['variable_maintenance'],
                            load_factor = cost_d_row['load_factor'],
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
                return group.sample(n=number)
            else:
                return group

        # select 5 random rows for each unique value in column A
        bld_df = df.groupby('Technology', group_keys=True).apply(select_random_rows)



        A = [self.generate_plant(a, cost_d, False, 0, 0, 0) for a in bld_df.itertuples()]
        return A

    def generate_storage_plants(self, company, df, number: dict):
        p_list = []
        for tech in number.keys():
            tech_data = df.loc[df['technology']==tech].iloc[0]
            plant = plants.StoragePlant(
                    name = f'{tech}',
                    technology=tech,
                    company_name=company,
                    capacity= number[tech],
                    production_capacity_MW_ratio=tech_data['production_capacity_MW'],
                    storage_capacity_MW_ratio= tech_data['storage_capacity_MW'],
                    reserve_capacity_MWh_ratio=tech_data['reserve_capacity_MWh'],
                    gen_eff = tech_data['eff_gen'],
                    store_eff = tech_data['eff_store'],
                    transmission_efficiency=tech_data['eff_transmission']
            )
            p_list.append(plant)
        return p_list 
