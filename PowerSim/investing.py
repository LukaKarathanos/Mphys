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
    def calculate_running_npv(plant: PowerPlant, discount_rate):
        '''Calculate npv'''


