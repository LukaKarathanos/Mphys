#%%
import pandas as pd
import data

df = pd.read_csv(r'C:\Users\LukaK\OneDrive - Durham University\Projects\Agent based modelling easy\PowerSim\DUKES_5.11.csv')

# %%

df.dropna(axis=0, how = 'all', inplace=True)

print((df.iloc[1312]))

# %%

data.DUKES_plants_df[data.DUKES_plants_df['Technology'] == 'Hydro']['installed_capacity_MW'].sum()

# %%


print(data.DUKES_plants_df['installed_capacity_MW'].sum())