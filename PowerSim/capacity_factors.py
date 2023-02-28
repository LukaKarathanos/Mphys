''' The capacity factors'''

import pandas as pd

merra_data = pd.read_csv(r'PowerSim/merra_2_data.csv')
merra_data.dropna(axis=0, how='all',inplace=True)


merra_data_days = merra_data.shape[0]/(24)
