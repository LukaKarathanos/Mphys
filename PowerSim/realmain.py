
import matplotlib.pyplot as plt
import matplotlib as mpl

from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np

from world_model import WorldModel
import data


def run():
    #initialise world
    list_of_plants = data.generate_plants_from_data(data.DUKES_plants_df, data.plant_costs_df)
    world = WorldModel(
            n_gen_cos = 3,
            power_plants=  list_of_plants,
            n_years = 20,
            n_days = 1
    )

    world.initialise_gen_cos()
    total_per_tech = []
    tech_types = ['nuclear', 'coal', 'fossil_fuel', 'bioenergy', 'wind_onshore', 'wind_offshore', 'solar', 'hydro', 'CCGT']


    for i in range(world.n_years):
        world.world_step()
        plant_list = world.get_plants()
        y_total_per_tech = []
        for tech in tech_types:
            energy = [(plant.energy_supplied_per_hour[-(24*world.n_days):]) for plant in plant_list if plant.technology == tech and len(plant.energy_supplied_per_hour) >= 24]
            energy = np.sum(energy, axis = 0)
            y_total_per_tech.append(energy)

        total_per_tech.append(y_total_per_tech)
        # print(world.get_demand())
        # print(f'year {i} complete')
        
    #The plot -> configured properly
    
    print('done')

    total_per_tech = np.array(total_per_tech)
    print(np.shape(total_per_tech))

    np.save('PowerSim/data_out/total_per_tech.npy', total_per_tech)

    return world.all_strike_prices, world.average_yearly_prices, world.n_years, total_per_tech 


if __name__ == '__main__':
    run()
