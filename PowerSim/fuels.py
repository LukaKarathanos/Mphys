from dataclasses import dataclass



gas_price = 50
'''gas price pounds per MWH. Could be highly variable'''
biomass_price = 75

coal_price = 18

'''price per ton/energy density. ~24MJ/kg -> 6.7MWH/ton. ~£120/ton'''

'''Do soon'''

@dataclass
class Fuel():
    '''
    Defines fuel types. Data for natural gas not LNG

    :fuel_type -  type of fuel used
    :fuel_price -  per MW
    :energy_density - MWh per tonne. net calorific value    
    :carbon_density - tonnes co2 eqv per tonne
    '''

    fuel_type: str
    fuel_price: float
    energy_density: float
    carbon_density: float

coal = Fuel('coal', 18, 6.71, 2.27045)
gas = Fuel('gas', 50, 12.55, 2.53925)
biomass = Fuel('biomass', 75, 4.8, 0)
none = Fuel('none', 0, 1, 0)

carbon_tax = 18.0



# def get_gas_price_per_MWh(year):


# def get_biomass_cost_per_MWh(year):