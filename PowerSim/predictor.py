''' 
Module containing classes to predict the future demand and the future electricity prices.
In future will have predictors for gas and carbon prices.
'''
from functools import lru_cache

import numpy as np
from sklearn.linear_model import LinearRegression
import pulp# import world_model
import time 

pulp.LpSolverDefault.msg = False
pulp.LpSolverDefault.timeLimit = 1

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
    
    @staticmethod
    # @lru_cache(maxsize=2000)
    def storage_production(NH, Emax, Smax, prices, h, R0, Rmax, eff_g, eff_st, f): 
        ts = time.time()       
        '''# number of hours
        NH: int = 48

        # max amount stored per hour
        Smax = 50
        # max amount produced per hour 
        Emax = 50

        # reservoir capacity
        Rmax = 500
        # reservoir initial reserves
        R0 = 250 

        #target fractional reserve
        f = 0.5

        # gen efficiency
        eff_g = 0.9

        # pump efficiency
        eff_st = 0.8

        # transmission efficiency 
        h = 0.95
        '''
        prob = pulp.LpProblem("MaximizeSum", pulp.LpMaximize)   

        # Define the decision variables - Amount of electricity produced at this hour 
        E = pulp.LpVariable.dicts("E", range(NH), lowBound=0, upBound=Emax)
        S = pulp.LpVariable.dicts("S", range(NH), lowBound=0, upBound=Smax)

        # Define the objective function
        prob += pulp.lpSum([prices[i] *(E[i]*h - S[i]*1/h)for i in range(NH)])

        # Define the constraints

        for k in range(NH):
            prob += (R0 + pulp.lpSum([S[i]*eff_st-E[i]*1/eff_g for i in range(k+1)])) <= Rmax
            prob += (R0 + pulp.lpSum([S[i]*eff_st- E[i]*1/eff_g for i in range(k+1)])) >= 0

        prob += pulp.lpSum([E[i]*1/eff_g -S[i]*eff_st for i in range(NH)]) == int(R0 -f*Rmax)
        

        # Solve the problem
        status = prob.solve()
        en = [pulp.value(E[i]-S[i]) for i in range(24)]

        # print(-(ts-time.time()))

        return en
    
        # # Print the solution
        # print("Status:", LpStatus[status])
        # print("Objective value:", value(prob.objective))
        # for i in range(NH):
        #     print(f'price {prices[i]}')
        #     print(f"E[{i}] = {value(E[i] - S[i])}")

    