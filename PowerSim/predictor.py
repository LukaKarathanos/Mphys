''' 
Module containing classes to predict the future demand and the future electricity prices.
In future will have predictors for gas and carbon prices.
'''
import numpy as np
from sklearn.linear_model import LinearRegression

# import world_model

class Forecast:
    ''' Class to forecast the price'''
    def __init__(self, model: 'world_model.WorldModel'):
        self.model = model

    @staticmethod
    def historical(historical_price_data: list, lookback_time: int = 5, lookforward_time: int = 20) -> np.ndarray:
        ''' Uses linear regression of historical data over the lookback time
        to forecast the spot price.'''
        prices = historical_price_data[-lookback_time:]
        y = np.array(prices)
        x = np.arange(-lookback_time,0).reshape((-1, 1))
        linreg = LinearRegression().fit(x,y)
        r_sq = linreg.score(x,y)
        predicted_future_prices = linreg.predict(np.arange(lookforward_time).reshape(-1, 1))
        return predicted_future_prices


    @staticmethod
    def demand(lookback_time: int = 5, lookforward_time: int = 20):
        '''this will change. '''