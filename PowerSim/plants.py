from abc import ABC
from dataclasses import dataclass, field
import random

import fuel_costs

@dataclass(order = True)
class PowerPlant(ABC): 
    '''
    name: plant name
    plant type:  the type of plant
    capacity: plant capacity in MW
    construction length: how many years takes to build
    construction date: year plant started operation
    operational_length: how long until plant needs to be shutdown
    variable_costs: cost to produce per MW - depends on fuel, need to implement
    fixed_costs: total fixed costs (maintance etc)
    build_costs: total cost to build
    load_factor: percentage of time they are available for 
    fuel_effeciency: what percent of fuel energy gets converted to electricity
    variable_maintenance: cost per MWh

    Should sort themselves by their variable costs -> could change this in future.
    '''
    # sort_index: float = field(init=False)
    name: str
    technology: str
    company: str
    capacity_MW: float
    construction_length: int = 5
    construction_date: int = 2022
    operational_length_years: float = 40
    variable_costs_per_MWH: float = 100
    fixed_costs_per_H: float = 10000
    build_costs: float = 200000000
    load_factor: float = 1.0
    fuel_effeciency: float = 1.0
    variable_maintenance_per_MWh: float = 5




    # def __post_init__(self):
    #     self.sort_index = self.variable_costs_per_MWH


    def calculate_lcoe(self) -> float:
        '''
        average total cost of building and operating the asset per unit of total electricity generated over the lifetime. 
        Price electricity needs to be to turn a profit. implement proper equation late with discount rate.  
        '''

        total_variable_costs = self.operational_length_years*8766*self.get_variable_costs()*self.capacity_MW 
        total_fixed_costs = self.operational_length_years*8766*self.fixed_costs_per_H
        lcoe = (self.build_costs + total_variable_costs + total_fixed_costs)/(self.capacity_MW*self.operational_length_years*8766)
        return lcoe
    
    def get_variable_costs(self) -> float:
        ''' Using the plant type calculate the variable costs'''
        if self.technology == 'Fossil Fuel':
            '''
            Generic fossil fuel
            Cost of fuel. Future add a little variation based on size maybe '''
            self.variable_costs_per_MWH = 100
            return 50

        elif self.technology == 'CCGT':
            c = fuel_costs.gas_price*1/self.fuel_effeciency + self.variable_maintenance_per_MWh
            self.variable_costs_per_MWH = c
            return c
        elif self.technology == 'Bioenergy':
            ''' cost of biomass'''
            c= fuel_costs.biomass_cost*1/self.fuel_effeciency  + self.variable_maintenance_per_MWh
            self.variable_costs_per_MWH  = c
            return c
        else:
            ''' others have no fuel cost '''
            c =  self.variable_maintenance_per_MWh
            self.variable_costs_per_MWH = c
            return c
            

# @dataclass(order=True)
# class FuelPowerPlant(PowerPlant):
    


# @dataclass(order=True)
# class PassivePowerPlant(PowerPlant):


# nuclear = PowerPlant('nuclear',capacity_MW = 3000, construction_date= 2022, operational_length_years = 40,
#                     variable_costs_per_MWH= 60, fixed_costs_per_H = 50000, build_costs= 200000000)

# gas = PowerPlant(name = 'gas')

# print(nuclear.build_costs)                    

# print(gas.calculate_lcoe())