''' Gets the data for the plants'''


import random
import pandas as pd

import plants



# def generate_plants(type_name: str,) -> list[plants.PowerPlant]:
#     ''' generate the data for the power plants '''


#     plant_list = []
#     for i in range(20):
#         var_costs_gas = random.uniform(60, 80)
#         age = random.randint(1985, 2022)
#         new_plant = plants.PowerPlant(
#                             f'{type_name} gas plant No. {i+1}',
#                             'ccgt', 800, 3,
#                             variable_costs_per_MWH = var_costs_gas,
#                             construction_date=age)
#         plant_list.append(new_plant)

#     for i in range(5):
#         var_costs_nuc = random.uniform(0.1, 2)
#         age = random.randint(1985, 2022)
#         new_plant = plants.PowerPlant(
#                                 f'{type_name} nuc plant No. {i+1}',
#                                 'nuc', 1200, 7,
#                                 variable_costs_per_MWH = var_costs_nuc,
#                                 construction_date=age)
#         plant_list.append(new_plant)
#     return plant_list

# #plants for the initial eleccos to use. Must be longer than the number of elec cos
# #list_of_plants = [generate_plants('Initial'), generate_plants('Initial'), generate_plants('Initial'), generate_plants('Initial')]




# def generate_more_plants(type_name: str,var_costs_gas = 80.0 , var_costs_nuc = 1.0) -> list:
#     ''' generates the data for the plants that can be built'''
#     plant_list = []
#     for i in range(30):
#         var_costs_gas = random.uniform(60, 80)
#         new_plant = plants.PowerPlant(f'{type_name} gas plant No. {i+1}', 'ccgt', 800, 3, variable_costs_per_MWH = var_costs_gas)
#         plant_list.append(new_plant)

#     for i in range(15):
#         var_costs_nuc = random.uniform(0.1, 2)
#         new_plant = plants.PowerPlant(f'{type_name} nuc plant No. {i+1}', 'nuc', 1200, 7,variable_costs_per_MWH = var_costs_nuc, build_costs= 15000000000, fixed_costs_per_H=20000)
#         plant_list.append(new_plant)

#     return(plant_list)


# buildable_plants = generate_more_plants('Buildable', 20, 0.1)

historical_price_data = [70.0, 70.0, 70.0, 70.0, 70.0]

DUKES_plants_df = pd.read_csv(r'C:\Users\LukaK\OneDrive - Durham University\Projects\Agent based modelling easy\PowerSim\DUKES_5.11.csv')
DUKES_plants_df.dropna(axis=0,how='all',inplace=True)

plant_costs_df = pd.read_csv(r'C:\Users\LukaK\OneDrive - Durham University\Projects\Agent based modelling easy\PowerSim\plant_cost_data.csv')             
plant_costs_df.dropna(axis=0, how='all', inplace=True)

def generate_plants_from_data(current_plant_database: pd.DataFrame, cost_d: pd.DataFrame) -> list[plants.PowerPlant]:
    ''' Generate plants from database.'''
    A = [
        plants.PowerPlant(
                        name=a.plant_name,
                        technology=a.Technology,
                        company = a.company_name,
                        capacity_MW=a.installed_capacity_MW,
                        construction_date=a.year_commissioned,  
                        operational_length_years= ((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['operating_lifetime']+10), 
                        fuel_effeciency = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fuel_effeciency'],
                        build_costs = (((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['construction_cost_medium'] 
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['pre-development_cost_medium'])*a.installed_capacity_MW 
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Infrastructure']*1000),
                        construction_length= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['total_construction_period'],
                        fixed_costs_per_H= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fixed_maintenance_costs']*a.installed_capacity_MW/8760
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Insurance']*a.installed_capacity_MW/8760      
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['connection_costs']*a.installed_capacity_MW/8760,
                        variable_maintenance_per_MWh= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['variable_maintenance'],
                        load_factor = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['load_factor']
        )

        for a in current_plant_database.itertuples()
    ]
    return A

def generate_buildable_plants_from_data(data: pd.DataFrame, cost_d: pd.DataFrame) -> list[plants.PowerPlant]:
    ''' Generate plants from database.'''
    A = [
        plants.PowerPlant(
                        name = f'Plant {a.Technology} number {i}',
                        company = 'None',
                        technology=a.Technology,
                        capacity_MW=a.installed_capacity_MW,
                        construction_date=a.year_commissioned,  
                        operational_length_years= ((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['operating_lifetime']+10), 
                        fuel_effeciency = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fuel_effeciency'],
                        build_costs= ((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['construction_cost_medium'] 
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['pre-development_cost_medium'])*a.installed_capacity_MW 
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Infrastructure']*1000,
                        construction_length= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['total_construction_period'],
                        fixed_costs_per_H= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fixed_maintenance_costs']*a.installed_capacity_MW/8760
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Insurance']*a.installed_capacity_MW/8760      
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['connection_costs']*a.installed_capacity_MW/8760,
                        variable_maintenance_per_MWh= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['variable_maintenance'],
                        load_factor = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['load_factor']
        )

        for i,a in enumerate(data.itertuples())
    ]
    return A





'''generate the data'''
plant_list = generate_plants_from_data(DUKES_plants_df, plant_costs_df)

buildable_plants = generate_buildable_plants_from_data(DUKES_plants_df, plant_costs_df)

# print(len(plant_list))
# print(set(df.Technology))
# print(set(df.company_name))

# print(set(df.primary_fuel))


