import numpy as np
from demand import hourly_demand_MW
from electricity_company import ElecCo
import data
import mesa
import elec_market
# class ElecModel(mesa.Model):
#     def __init__(self):
#         elec_co = ElecCo('edf', data.list_of_plants)
        

#     def step(self):
#         """Advance the model by one step."""
#         self.schedule.step()
        

def run(n_steps):
    elec_co = ElecCo('edf', data.list_of_plants)
    market = elec_market.Market()
    # print(elec_co.plants)
    all_strike_prices = []
    daily_strike_prices = []
    bids = elec_co.plants
    for i in range(n_steps):           
        bids.sort()

        for n, demand,in enumerate(hourly_demand_MW):
            print(demand)
            daily_strike_prices += [market.fill_demand(demand, elec_co.plants)[0]]
        all_strike_prices += [daily_strike_prices]
        average_strike_price = sum(daily_strike_prices)/len(daily_strike_prices)
        elec_co.step(average_strike_price)
        print(f'the strike prices on day {i} are {daily_strike_prices}')



if __name__ == '__main__':
    run(4)
