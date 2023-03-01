import random
import time 
import os
import sys 

import numpy as np
import pickle
import multiprocessing
import functools

from world_model import WorldModel
import data

current_time = int(time.time())
process_id = os.getpid()

if len(sys.argv) > 1:
    job_id = sys.argv[1]
else:
    job_id = process_id



seed = current_time * job_id
random.seed(seed)

def run(
        plant_data, 
        plant_cost_data,
        n_years,
        n_days,
        seed=None
):
    #initialise world. generate the plants
    if seed is not None:
        random.seed(seed)
        
    list_of_plants = data.generate_plants_from_data(plant_data, plant_cost_data)

    buildable_plants = data.generate_buildable_plants_from_data(plant_data, plant_cost_data)

    world = WorldModel(
            power_plants =  list_of_plants,
            buildable_plants = buildable_plants,
            n_years = n_years,
            n_days = n_days
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
        #print(f'year {i} complete')

    #The plot -> configured properly
    
    # obj_list = world.get_elec_cos()
    # with open('powerplants.pickle', 'wb') as f:
    #     pickle.dump(obj_list, f)

    #print('done')

    total_per_tech = np.array(total_per_tech)
    all_strike_prices = np.array(world.all_strike_prices)
    #print(np.shape(total_per_tech))

    np.save(f'data/36days/tech/total_per_tech_{job_id}.npy', total_per_tech)
    np.save(f'data/36days/price/all_strike_prices_{job_id}.npy', all_strike_prices)

    return total_per_tech  #world.all_strike_prices, world.average_yearly_prices, 


'''
run once
'''

if __name__ == '__main__':
    n_years = 30
    n_days = 36
    run(data.DUKES_plants_df,
        data.plant_costs_df,
        n_years,
        n_days)


''' Run many'''

# if __name__ == '__main__':
#     num_runs = 1
#     seeds = [random.randint(0, 1000000) for _ in range(num_runs)] 
#     n_years = 10
#     n_days = 4

#     args =  (data.DUKES_plants_df,
#         data.plant_costs_df,
#         n_years,
#         n_days)    
    
#     partial_func = functools.partial(run, *args)

#     with multiprocessing.Pool() as pool:
#         results = pool.map(partial_func, range(num_runs))
#         results = np.array(results)
#         np.save('data_out/results.npy', results)
