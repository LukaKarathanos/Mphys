from dataclasses import dataclass
import random



'''Do soon'''

@dataclass
class Fuel():
    '''
    Defines fuel types. Data for natural gas not LNG

    :fuel_type -  type of fuel used
    :fuel_price -  per MWh
    :energy_density - MWh per tonne. net calorific value    
    :carbon_density - tonnes co2 eqv per tonne
    :capacity factor - the days capacity factor 
    '''

    fuel_type: str
    fuel_price: float
    energy_density: float
    carbon_density: float   
    price_increase_per_year: float = 1
    price_stdev: float = 0
    mean_fuel_price: float = None
    fuel_price_history = []

    def __post_init__(self):
        self.mean_fuel_price = self.fuel_price
        self.fuel_price_history = [self.fuel_price]*10

    def set_fuel_price(self) -> None:
        ''' get fuel price for the year. Runs every step'''
        self.mean_fuel_price = self.price_increase_per_year*self.mean_fuel_price
        fp = random.normalvariate(self.mean_fuel_price, self.price_stdev)
        self.fuel_price = fp        

coal = Fuel(fuel_type = 'coal', fuel_price= 25, energy_density=6.71, carbon_density =2.27045, price_increase_per_year = 1.01, price_stdev=2)
gas = Fuel(fuel_type = 'gas', fuel_price= 25, energy_density=12.55, carbon_density = 2.53925, price_increase_per_year = 1.01, price_stdev=2)
biomass = Fuel('biomass', 20, 4.8, 0)
none = Fuel('none', 0, 1, 0)

fuel_list = [coal, gas, biomass, none]

@dataclass
class CarbonTax():
    carbon_tax: float
    exponential_tax_increase: float = 1
    def set_carbon_tax(self, year: int):
        self.carbon_tax = self.exponential_tax_increase**(year)*self.carbon_tax 

carbon_tax = CarbonTax(50, 1.02)
# def get_gas_price_per_MWh(year):


# def get_biomass_cost_per_MWh(year):