import random
import time 
import os
import sys 

import numpy as np

import pandas as pd 

from world_model import WorldModel
import plant_data


current_time = int(time.time())
process_id = os.getpid()
if len(sys.argv) > 1:
    job_id = sys.argv[1]
else:
    job_id = process_id


seed = current_time * job_id
random.seed(seed)

def run(
        plant_data_df, 
        plant_cost_data,
        storage_data, 
        storage_co_n,
        n_years,
        n_days,
        seed=None
):
    if not os.path.exists(f'data/{scenario_name}'):
        raise FileNotFoundError(f"The folder '{scenario_name}' does not exist.")



    #initialise world. generate the plants
    if seed is not None:
        random.seed(seed)

    plant_generator = plant_data.plant_generator()    

    list_of_plants = plant_generator.generate_plants_from_data(plant_data_df, plant_cost_data, ol_extension=10)

    storage_plants = []
    for co in range(storage_co_n):
        number  = {'pumped_hydro': 250, 
                   'battery':250
                   }
        storage_plants.extend(plant_generator.generate_storage_plants(co, storage_data, number))

    world = WorldModel(
            power_plants =  list_of_plants,
            storage_plants = storage_plants,
            buildable_plant_data = plant_data_df,
            plant_cost_data = plant_cost_data,
            n_years = n_years,
            n_days = n_days,
            storage_co_n=storage_co_n,
            yearly_storage_increase=1000
    )

    #world.initialise_gen_cos()
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
        print(f'year {i} complete')


    #The plot -> configured properly
    
    # obj_list = world.get_elec_cos()
    # with open('powerplants.pickle', 'wb') as f:
    #     pickle.dump(obj_list, f)

    #print('done')

    total_per_tech = np.array(total_per_tech)
    all_strike_prices = np.array(world.all_strike_prices)

    monies = np.array([genco.cash for genco in world.get_elec_cos()])
    #print(np.shape(total_per_tech))

    np.save(f'data/{scenario_name}/{job_id}_total_per_tech.npy', total_per_tech)
    np.save(f'data/{scenario_name}/{job_id}_all_strike_prices.npy', all_strike_prices)
    np.save(f'data/{scenario_name}/{job_id}monies.npy', monies)

    storage_list = world.storage_plants
    for i, obj in enumerate(storage_list):
        ls = obj.energy_supplied_per_hour
        if i ==0:
            df = pd.DataFrame({f'{i+1}{obj.name}':ls})
        else:
            df[f'{i+1}{obj.name}'] = ls


    

    df.to_csv(f'data/{scenario_name}/{job_id}_storage_plant_prod.csv', index = False)

    return total_per_tech  #world.all_strike_prices, world.average_yearly_prices, 


'''
run once
'''

if __name__ == '__main__':
    n_years = 30
    n_days = 8
    storage_co_n = 6
    scenario_name = 'demand_increasing'

    start_time = time.time()

    run(plant_data.DUKES_plants_df,
        plant_data.plant_costs_df,
        plant_data.storage_data_df,
        storage_co_n,
        n_years,
        n_days)
    
    end_time = time.time()

    print(f'Elapsed time: {start_time-end_time}s')

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
