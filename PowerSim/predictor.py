''' 
Module containing classes to predict the future demand and the future electricity prices. 
In future will have predictors for gas and carbon prices. 
'''
import numpy as np
from sklearn.linear_model import LinearRegression 

import world_model

class ForecastSpotPrice:
    ''' Class to forecast the price'''
    def __init__(self, model: world_model.WorldModel):
        self.model = model
        self.historical_strike_prices = model.average_yearly_prices
        
    def historical(self, lookback_time: int = 5, lookforward_time: int = 20):
        ''' Uses linear regression of historical data over the lookback time 
        to forecast the spot price.'''
        prices = self.historical_strike_prices[-lookback_time:]
        y = np.array(prices)
        x = np.arange(-5,0).reshape((-1, 1))
        linreg = LinearRegression().fit(x,y)
        r_sq = linreg.score(x,y)
        print(r_sq)
        predicted_future_prices = linreg.predict(np.arange(lookforward_time))
        return(predicted_future_prices)

    def market(self):
        '''Runs the electricity market to forecast the spot price'''
