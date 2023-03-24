import numpy as np
import numpy_financial as npf

from plants import PowerPlant


class ProfitCalculator:
    def __init__(self, model):
        self.model = model

    @staticmethod
    def calculate_npv(plant:PowerPlant, forecast_average_prices: np.ndarray, discount_rate: float = 0.05) -> float:
        ''' Using forecast yearly electricity costs, calculate the expected profit of the plants. Assumes plant always runs. 
        Need to change.
        '''
        lcoe = plant.calculate_lcoe()
        cash_flow = forecast_average_prices*8760.25*plant.capacity_MW - lcoe
        cash_flow = np.insert(cash_flow, 0, -plant.build_costs)
        npv = npf.npv(discount_rate, cash_flow)
        return npv
    
    @staticmethod
    def calculate_npv_proper(plant: PowerPlant, forecast_cashflow, discount_rate: float = 0.05) -> float:
        '''Calculates NPV per mw of capacity'''
        cashflow = np.full(plant.operational_length_years, forecast_cashflow)
        buildcost_cashflow = np.full(plant.construction_length, -plant.build_costs/plant.construction_length)
        cashflow = np.insert(cashflow, 0, buildcost_cashflow)
        npv = npf.npv(discount_rate, cashflow)
        return npv
    
    @staticmethod
    def calculate_running_npv(plant: PowerPlant, discount_rate):
        '''Calculate npv'''

    @staticmethod
    def calculate_yearly_debt(plant: PowerPlant, downpayment_percent, interest_rate):
        total_debt = (1-downpayment_percent)*plant.build_costs
        rate = npf.pmt(interest_rate, (plant.operational_length_years+plant.construction_length),total_debt)
        return rate
    

