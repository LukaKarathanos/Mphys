#%%

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)


from realmain import all_plants, all_prices, elec_company_history, plant_his 
import data




# %% 

tech_types = ['nuclear', 'coal', 'fossil_fuel', 'bioenergy', 'wind_onshore', 'wind_offshore', 'solar', 'hydro', 'CCGT']
total_per_tech = []
total_per_tech24 = []
for t in tech_types:
    energy = [(plant.energy_supplied_per_hour) for plant in plant_his if plant.technology == t]
    energy2 = np.sum(energy, axis = 0)
    total_per_tech.append(energy2)
    # total_per_tech24.append(energy2[:24])
    #total_per_tech.append(total)


# %%

print(len(total_per_tech[0]))

print(tech_types[1])

print(set(data.DUKES_plants_df.Technology))
#%%
'''Stacked plot of daily production'''

# tech_types = set(data.DUKES_plants_df['Technology'])



#%%
    

fig, ax = plt.subplots()

ydata = [total_per_tech]
print(ydata)

ax.stackplot(range(len(ydata[1])), *ydata, labels = [t for t in tech_types])
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

plt.savefig(fname = 'first working daily production plot')
plt.show()


# %%