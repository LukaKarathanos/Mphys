#%%


import numpy as np
from demand import hourly_demand_MW
from electricity_company import ElecCo
import data
import mesa
import elec_market
import world_model 
import matplotlib.pyplot as plt
# class ElecModel(mesa.Model):
#     def __init__(self):
#         elec_co = ElecCo('edf', data.list_of_plants)
        

#     def step(self):
#         """Advance the model by one step."""
#         self.schedule.step()
        

def run(n_years, n_days):
    '''
    Iterates over the number of years -> the timestep. 
    Each year the market is calculated for n days to simulate the yearly demand.
    '''  
    model = world_model.WorldModel(2022)
    elec_co = ElecCo('edf', data.list_of_plants)
    market = elec_market.Market()
    # print(elec_co.plants)
    all_strike_prices = []
    average_yearly_strike_prices = []
    for j in range(n_years):
        average_daily_prices = []
        for i in range(n_days):     
            daily_strike_prices = []
            for n, demand,in enumerate(hourly_demand_MW):        
                bids = elec_co.power_plants
                bids.sort()
                price, plants_selected = market.fill_demand(demand, bids)
                daily_strike_prices += [price]
            all_strike_prices += [daily_strike_prices]
            average_daily_prices += [sum(daily_strike_prices)/len(daily_strike_prices)]
        average_yearly_strike_prices += [sum(average_daily_prices)/len(average_daily_prices)]
        elec_co.step(average_yearly_strike_prices[j], model.current_year)
        for plant in elec_co.build_queue:
            if (plant.construction_date + plant.construction_length) <= model.current_year:
                elec_co.power_plants.append(plant)
                elec_co.build_queue.remove(plant)
                print(f'finished building {plant}')
        model.current_year += 1


    print(average_yearly_strike_prices)

    fig, ax = plt.subplots()
    ax.plot(range(n_years), average_yearly_strike_prices)
    plt.show

#number of representative days within the year.
n_days = 4
n_years = 30

#%%
if __name__ == '__main__':

    run(n_years,n_days)

# %%
