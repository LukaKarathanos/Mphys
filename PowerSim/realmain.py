#%%
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import numpy as np

from world_model import WorldModel
import data

''' Format plots'''

fsize = 11
tsize = 12
tdir = 'in'
major = 5.0
minor = 3.0
lwidth = 0.8
lhandle = 2.0
plt.style.use('default')
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = fsize
plt.rcParams['legend.fontsize'] = tsize
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
plt.tight_layout()



def run():
    #initialise world
    list_of_plants = data.generate_plants_from_data(data.DUKES_plants_df, data.plant_costs_df)
    world = WorldModel(
            n_gen_cos = 3,
            power_plants=  list_of_plants,
            n_years = 10
    )

    world.initialise_gen_cos()
    for i in range(world.n_years):
        world.world_step()


        #The plot -> configured properly
    
    fig, ax = plt.subplots()
    ax.plot(range(world.n_years), world.average_yearly_prices[5:])
    #have to remove the historical data from the plot
    ax.set_ylabel('Average price per MWh (£)')
    ax.set_xlabel('Year')
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    # ax.set_xlim(0, n_years)
    # ax.set_ylim(min(average_yearly_strike_prices) - 5, (max(average_yearly_strike_prices) + 5))
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    plt.show()
    print('done')
    return world.all_plants_selected, world.all_strike_prices    


#%%
# if __name__ == '__main__':
#     all_plants, all_prices = run()

all_plants, all_prices = run()

# %%
'''Stacked plot of daily production'''

tech_types = set(data.DUKES_plants_df['Technology'])

tech_types = ['Nuclear', 'Coal', 'Fossil Fuel', 'Bioenergy', 'wind_onshore', 'wind_offshore', 'Solar', 'Hydro', 'CCGT']
per_tech_summed = []
for plants_active_per_hour in all_plants[-1]:
    supplied_per_tech = {}
    for t in tech_types:
        supplied_per_tech[t] = (np.array([p.capacity_MW*p.load_factor for p in plants_active_per_hour if p.technology == t]).sum())
    per_tech_summed.append(supplied_per_tech)

#print(per_tech_summed)

#%%
fig, ax = plt.subplots()

ydata = []
for t in tech_types:
    d = [m[t] for m in per_tech_summed]
    ydata.append(d)
ax.stackplot(range(len(per_tech_summed)), *ydata, labels = [t for t in tech_types])
#have to remove the historical data from the plot

ax.set_ylabel('Production (MW)')
ax.set_xlabel('Hour')
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.yaxis.set_minor_locator(AutoMinorLocator())
ax.legend()
# ax.set_xlim(0, n_years)
# ax.set_ylim(min(average_yearly_strike_prices) - 5, (max(average_yearly_strike_prices) + 5))
ax.spines.right.set_visible(False)
ax.spines.top.set_visible(False)

plt.show()


# %%
