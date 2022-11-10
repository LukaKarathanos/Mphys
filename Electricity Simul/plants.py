from abc import ABC
from dataclasses import dataclass, field
import random

@dataclass(order = True)
class PowerPlant(ABC): 

    sort_index: float = field(init=False)
    name: str
    plant_type: str
    capacity_MW: float
    construction_length: int
    construction_date: int = 2022
    operational_length_years: float = 40
    variable_costs_per_MWH: float = 100
    fixed_costs_per_H: float = 10000
    build_costs: float = 200000000
    def __post_init__(self):
        self.sort_index = self.variable_costs_per_MWH
    '''
    name - plant name
    plant type -  the type of plant
    capacity - plant capacity in MW
    construction length - how many years takes to build
    construction date - year plant started operation
    operational_length - how long until plant needs to be shutdown
    variable_costs - cost to produce per MW - depends on fuel, need to implement 
    fixed_costs - total fixed costs (maintance etc)
    build_costs - total cost to build

    Should sort themselves by their variable costs -> could change this in future. 
    '''

    def calculate_lcoe(self):
        '''
        average total cost of building and operating the asset per unit of total electricity generated over the lifetime. 
        Price electricity needs to be to turn a profit. implement proper equation late with discount rate.  
        '''

        total_variable_costs = self.operational_length_years*8766*self.variable_costs_per_MWH*self.capacity_MW 
        total_fixed_costs = self.operational_length_years*8766*self.fixed_costs_per_H
        lcoe = (self.build_costs + total_variable_costs + total_fixed_costs)/(self.capacity_MW*self.operational_length_years*8766)
        return lcoe
    


# @dataclass(order=True)
# class FuelPowerPlant(PowerPlant):
    


# @dataclass(order=True)
# class PassivePowerPlant(PowerPlant):


# nuclear = PowerPlant('nuclear',capacity_MW = 3000, construction_date= 2022, operational_length_years = 40,
#                     variable_costs_per_MWH= 60, fixed_costs_per_H = 50000, build_costs= 200000000)

# gas = PowerPlant(name = 'gas')

# print(nuclear.build_costs)                    

# print(gas.calculate_lcoe())