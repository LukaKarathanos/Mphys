''' Gets the data for the plants'''


import random
import pandas as pd

import plants



historical_price_data = [70.0, 70.0, 70.0, 70.0, 70.0]

DUKES_plants_df = pd.read_csv(r'PowerSim/DUKES_5.11.csv')
DUKES_plants_df.dropna(axis=0,how='all',inplace=True)

plant_costs_df = pd.read_csv(r'PowerSim/plant_cost_data.csv')             
plant_costs_df.dropna(axis=0, how='all', inplace=True)


def generate_plants_from_data(current_plant_database: pd.DataFrame, cost_d: pd.DataFrame):
    ''' Generate plants from database.'''
    A = [
        plants.PowerPlant(
                        name=a.plant_name,
                        technology=a.Technology,
                        company = a.company_name,
                        capacity_MW=a.installed_capacity_MW,
                        construction_start_date=a.year_commissioned,  
                        construction_end_date= a.year_commissioned,
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
                        load_factor = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['load_factor'],
                        is_operating=True
        )

        for a in current_plant_database.itertuples()
    ]
    return A

def generate_buildable_plants_from_data(buildable_plant_database: pd.DataFrame, cost_d: pd.DataFrame):
    ''' Generate plants from database.'''
    A = [
        plants.PowerPlant(
                        name = f'Plant {a.Technology} number {i}',
                        technology=a.Technology,
                        company = 'None',
                        capacity_MW=a.installed_capacity_MW,
                        operational_length_years= ((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['operating_lifetime']), 
                        fuel_effeciency = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fuel_effeciency'],
                        build_costs= (((cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['construction_cost_medium'] 
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['pre-development_cost_medium'])*a.installed_capacity_MW 
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Infrastructure']*1000),
                        construction_length= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['total_construction_period'],
                        fixed_costs_per_H= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['fixed_maintenance_costs']*a.installed_capacity_MW/8760
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['Insurance']*a.installed_capacity_MW/8760      
                                    + (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['connection_costs']*a.installed_capacity_MW/8760,
                        variable_maintenance_per_MWh= (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['variable_maintenance'],
                        load_factor = (cost_d[cost_d['Technology'] == a.Technology]).iloc[0]['load_factor'],
                        is_operating=False
        )

        for i,a in enumerate(buildable_plant_database.itertuples())
    ]
    return A






