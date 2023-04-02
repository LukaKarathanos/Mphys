#%%
import pandas as pd
import numpy as np
import pytz



import glob

# Get a list of all CSV files in a directory
path = 'demand_data/*.csv'
csv_files = sorted(glob.glob(path))

# Read all CSV files into a list of DataFrames
dfs = []
for csv_file in csv_files:
    df = pd.read_csv(csv_file, usecols=['SETTLEMENT_DATE', 'SETTLEMENT_PERIOD', 'ND',
                                        'TSD', 'ENGLAND_WALES_DEMAND','EMBEDDED_WIND_GENERATION',	
                                        'EMBEDDED_WIND_CAPACITY','EMBEDDED_SOLAR_GENERATION',
                                        'EMBEDDED_SOLAR_CAPACITY'])
    df['ND_and_renewables'] = df['ND']+df['EMBEDDED_WIND_GENERATION']+df['EMBEDDED_SOLAR_GENERATION']
    df['normalised_demand'] = df['ND_and_renewables']/df['ND_and_renewables'].mean()
    dfs.append(df)

# Concatenate all DataFrames vertically
df = pd.concat(dfs, axis=0, ignore_index=True)

#%%

print(df.dtypes)

df['group'] = (df.index // 2)

df = df.groupby('group').mean()


# Define the start and end dates
start_date = pd.Timestamp('2011-01-01 00:00:00', tz='Europe/London')
end_date = pd.Timestamp('2023-01-01 00:00:00', tz='Europe/London')

# Create a datetime index with hourly frequency and local timezone
date_range = pd.date_range(start=start_date, end=end_date, freq='H', tz='Europe/London', inclusive='left')

# Convert the datetime index to a DataFrame with a single column
df['bst_dates']=date_range
df['utc_dates']=df['bst_dates'].dt.tz_convert('UTC')
df['SETTLEMENT_DATE'] = df['utc_dates']
df = df.drop('bst_dates', axis=1)
df = df.drop('utc_dates', axis=1)
df.to_csv('hist_demand_data.csv', index=False)

# %%