import random
import plants
import pickle



def generate_plants(type_name: str,) -> list:
    ''' generate the data for the power plants '''

    list_of_plants = []
    for i in range(20):
        var_costs_gas = random.uniform(60, 80)
        age = random.randint(1985, 2022)
        new_plant = plants.PowerPlant(f'{type_name} gas plant No. {i+1}', 'ccgt', 800, 3, variable_costs_per_MWH = var_costs_gas, construction_date=age)
        list_of_plants.append(new_plant)

    for i in range(5):
        var_costs_nuc = random.uniform(0.1, 2)
        age = random.randint(1985, 2022)
        new_plant = plants.PowerPlant(f'{type_name} nuc plant No. {i+1}', 'nuc', 1200, 7, variable_costs_per_MWH = var_costs_nuc, construction_date=age)
        list_of_plants.append(new_plant)
    return(list_of_plants)


list_of_plants = generate_plants('Initial')




def generate_more_plants(type_name: str,var_costs_gas = 80.0 , var_costs_nuc = 1.0) -> list:
    list_of_plants = []
    for i in range(30):
        var_costs_gas = random.uniform(60, 80)
        new_plant = plants.PowerPlant(f'{type_name} gas plant No. {i+1}', 'ccgt', 800, 3, variable_costs_per_MWH = var_costs_gas)
        list_of_plants.append(new_plant)

    for i in range(15):
        var_costs_nuc = random.uniform(0.1, 2)
        new_plant = plants.PowerPlant(f'{type_name} nuc plant No. {i+1}', 'nuc', 1200, 7,variable_costs_per_MWH = var_costs_nuc, build_costs= 15000000000, fixed_costs_per_H=20000)
        list_of_plants.append(new_plant)

    return(list_of_plants)


buildable_plants = generate_more_plants('Buildable', 20, 0.1)
 