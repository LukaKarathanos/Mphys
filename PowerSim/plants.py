from abc import ABC
from dataclasses import dataclass, field
import random
import numpy as np

import fuels
from capacity_factors import capacity_factors

@dataclass(init=True, order = True)
class PowerPlant(): 
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
    energy_supplied_per_hour: data of energy they supply
    is_operating
    Should sort themselves by their variable costs -> could change this in future.
    '''
    # sort_index: float = field(init=False)
    name: str
    technology: str
    company: str
    capacity_MW: float

    construction_length: int = 5
    construction_start_date: int = 2023
    construction_end_date: int = 2023
    operational_length_years: float = 40
    variable_costs_per_MWH: float = 100
    fixed_costs_per_H: float = 10000
    build_costs: float = 200000000
    load_factor: float = 1.0
    fuel_effeciency: float = 1.0
    variable_maintenance_per_MWh: float = 5
    energy_supplied_per_hour: list = field(default_factory=lambda:[])
    is_operating: bool = False
    interest_rate = 0.075
    yearly_debt_payment = 0
    npv = None
    being_built = False
    capacity_factors = capacity_factors

    def __post_init__(self):
        self.sort_index = self.variable_costs_per_MWH
        self.fuel = self.get_fuels(self.technology)
        self.load_factors = np.full(24, self.load_factor)


    def get_fuels(self, technology) -> fuels.Fuel:
        ''' sets the fuel type for the plant'''
        if technology == 'CCGT':
            return fuels.gas
        elif technology == 'coal':
            return fuels.coal
        elif technology == 'bioenergy':
            return fuels.biomass
        elif technology == 'fossil_fuel':
            return fuels.coal
        else:
            return fuels.none


    def calculate_lcoe(self) -> float:
        '''
        average total cost of building and operating the asset per unit of total electricity generated over the lifetime. 
        Price electricity needs to be to turn a profit. implement proper equation late with discount rate.  
        '''

        total_variable_costs = self.operational_length_years*8766*self.get_variable_costs()*self.capacity_MW*self.load_factor 
        total_fixed_costs = self.operational_length_years*8766*self.fixed_costs_per_H
        lcoe = (self.build_costs + total_variable_costs + total_fixed_costs)/(self.capacity_MW*self.load_factor*self.operational_length_years*8766)
        return lcoe

    def get_variable_costs(self) -> float:
        ''' Using the plant type calculate the variable costs'''

        if self.technology == 'CCGT' or self.technology == 'bioenergy' or self.technology == 'coal' or self.technology == 'fossil_fuel':
            c = (self.fuel.fuel_price + self.get_carbon_tax())*1/self.fuel_effeciency + self.variable_maintenance_per_MWh
            return c

        else:
            ''' others have no fuel cost '''
            c =  self.variable_maintenance_per_MWh
            return c
            
    def get_capacity_factor(self, technology, day=None) -> np.ndarray:
        '''returns the load factors for the current day. Input a random valid date'''
        if day is not None:
            if technology in ['solar', 'wind_onshore', 'wind_offshore']:
                cf = self.capacity_factors.merra_data[technology].iloc[day*24:day*24+24].values
                return cf
            else:
                return self.load_factors
        else:
            if technology in ['solar', 'wind_onshore', 'wind_offshore']:
                cf = self.capacity_factors.capacity_fact_dict[technology]
                return cf
            else:
                return self.load_factors

    def get_carbon_tax(self):
        ''' Tax per mwh of fuel used'''
        carbon_per_mwh = self.fuel.carbon_density/self.fuel.energy_density
        tax_per_mwh = fuels.carbon_tax.carbon_tax*carbon_per_mwh
        return tax_per_mwh

