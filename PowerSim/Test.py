#%%
import pandas as pd
import data

df = pd.read_excel(r'C:\Users\LukaK\OneDrive - Durham University\Projects\Agent based modelling easy\PowerSim\plant_cost_data.xlsx',
                        sheet_name='Sheet2')

# %%


print(df['Technology'])
# %%

data.DUKES_plants_df[data.DUKES_plants_df['Technology'] == 'Hydro']['installed_capacity_MW'].sum()

# %%


print(data.DUKES_plants_df['installed_capacity_MW'].sum())