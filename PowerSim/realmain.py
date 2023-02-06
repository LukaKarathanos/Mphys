#%%
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np

from world_model import WorldModel
import data


''' Format plots'''

fsize = 11
tsize = 18
tdir = 'in'
major = 5.0
minor = 3.0
lwidth = 0.8
lhandle = 2.0
plt.style.use('default')
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = fsize
plt.rcParams['legend.fontsize'] = fsize
plt.rcParams['xtick.direction'] = tdir
plt.rcParams['ytick.direction'] = tdir
plt.rcParams['xtick.major.size'] = major
plt.rcParams['xtick.minor.size'] = minor
plt.rcParams['ytick.major.size'] = 5.0
plt.rcParams['ytick.minor.size'] = 3.0
plt.rcParams['axes.linewidth'] = lwidth
plt.rcParams['legend.handlelength'] = lhandle
plt.rcParams['axes.autolimit_mode'] = 'round_numbers'
plt.rcParams['axes.xmargin'] = 0
plt.rcParams['axes.ymargin'] = 0

def run():
    #initialise world
    list_of_plants = data.generate_plants_from_data(data.DUKES_plants_df, data.plant_costs_df)
    world = WorldModel(
            n_gen_cos = 3,
            power_plants=  list_of_plants,
            n_years = 5
    )

    world.initialise_gen_cos()
    total_per_tech = []
    tech_types = ['nuclear', 'coal', 'fossil_fuel', 'bioenergy', 'wind_onshore', 'wind_offshore', 'solar', 'hydro', 'CCGT']


    for i in range(world.n_years):
        world.world_step()
        current_plant_list = world.get_plants()
        y_total_per_tech = []
        for tech in tech_types:
            energy = [(plant.energy_supplied_per_hour[-(24*world.n_days):]) for plant in current_plant_list if plant.technology == tech and len(plant.energy_supplied_per_hour) > 0]
            energy = np.sum(energy, axis = 0)
            y_total_per_tech.append(energy)

        total_per_tech.append(y_total_per_tech)
        print(f'year {i} complete')
        
    #The plot -> configured properly
    
    print('done')


    return world.all_strike_prices, world.average_yearly_prices, world.n_years, total_per_tech 


#%%
# if __name__ == '__main__':
#     all_plants, all_prices = run()

all_prices, average_yearly_prices, n_years, total_per_tech = run()




# %% 

tech_types = ['nuclear', 'coal', 'fossil_fuel', 'bioenergy', 'wind_onshore', 'wind_offshore', 'solar', 'hydro', 'CCGT']
# total_per_tech = []
# total_per_tech24 = []
# for t in tech_types:
#     energy = [(plant.energy_supplied_per_hour) for plant in plant_his if plant.technology == t]
#     energy2 = np.sum(energy, axis = 0)
#     total_per_tech.append(energy2)
#     # total_per_tech24.append(energy2[:24])
#     #total_per_tech.append(total)

#%%
'''Stacked plot of daily production'''

# tech_types = set(data.DUKES_plants_df['Technology'])

print(len(total_per_tech[4][4]))


#%%
    

fig, ax = plt.subplots()

total_per_tech = np.array(total_per_tech)
print(np.shape(total_per_tech))

ydata = total_per_tech[0,:9, :24]
print(np.shape(ydata))
# print(ydata)
tech_types_named =  ['Nuclear', 'Coal', 'Other fossil fuel','Biomass', 'Onshore wind', 'Offshore wind', 'Solar', 'Hydro', 'Gas']
ax.stackplot(range((24)), *ydata, labels = [t for t in tech_types_named])
#have to remove the historical data from the plot

ax.set_ylabel('Production (MW)')
ax.set_xlabel('Hour')
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.legend(loc = (1.04, 0.25))
# ax.set_xlim(0, n_years)
# ax.set_ylim(min(average_yearly_strike_prices) - 5, (max(average_yearly_strike_prices) + 5))
ax.spines.right.set_visible(False)
ax.spines.top.set_visible(False)

plt.savefig(fname = 'first working daily production plot')
plt.show()
