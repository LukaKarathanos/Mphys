import random
import plants
import pickle

''' generate the data for the power plants '''


def generate_plants(type_name: str,) -> list:
    list_of_plants = []
    for i in range(30):
        var_costs_gas = random.uniform(80, 120)
        new_plant = plants.PowerPlant(f'{type_name} gas plant No. {i+1}', variable_costs_per_MWH = var_costs_gas)
        list_of_plants.append(new_plant)

    for i in range(15):
        var_costs_nuc = random.uniform(0.1, 2)
        new_plant = plants.PowerPlant(f'{type_name} nuc plant No. {i+1}', variable_costs_per_MWH = var_costs_nuc)
        list_of_plants.append(new_plant)
    return(list_of_plants)


list_of_plants = generate_plants('Initial')




def generate_more_plants(type_name: str,var_costs_gas, var_costs_nuc) -> list:
    list_of_plants = []
    for i in range(30):
        new_plant = plants.PowerPlant(f'{type_name} gas plant No. {i+1}', variable_costs_per_MWH = var_costs_gas)
        list_of_plants.append(new_plant)

    for i in range(15):
        new_plant = plants.PowerPlant(f'{type_name} nuc plant No. {i+1}', variable_costs_per_MWH = var_costs_nuc)
        list_of_plants.append(new_plant)

    return(list_of_plants)


buildable_plants = generate_more_plants('Buildable', 20, 0.1)
 