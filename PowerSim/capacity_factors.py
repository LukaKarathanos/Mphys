''' The capacity factors'''

import pandas as pd
from dataclasses import dataclass



@dataclass
class CapacityFactors:
    merra_data: pd.DataFrame

    def __post_init__(self):
        self.merra_data_days = self.merra_data.shape[0]/(24)
        self.capacity_fact_dict ={'solar':None ,
                                   'wind_onshore':None,
                                   'wind_offshore':None
        }
        self.merra_data.dropna(axis=0, how='all',inplace=True)

    
    
    def set_daily_cfs(self, day):
            for technology in ['solar', 'wind_onshore', 'wind_offshore']:
                self.capacity_fact_dict[technology] = self.merra_data[technology].iloc[day*24:day*24+24].values


merra_data = pd.read_csv(r'PowerSim/merra_2_data.csv')

capacity_factors = CapacityFactors(merra_data)