from abc import ABC
from dataclasses import dataclass, field
from functools import lru_cache
import random
import numpy as np

import fuels
from capacity_factors import capacity_factors
from predictor import Forecast

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
    company_name: str
    capacity_MW: float
    
    company = None 
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
            c = (self.fuel.fuel_price + self.get_carbon_tax(self.fuel))*1/self.fuel_effeciency + self.variable_maintenance_per_MWh
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

    def get_carbon_tax(self, fuel:fuels.Fuel):
        ''' Tax per mwh of fuel used'''
        carbon_per_mwh = fuel.carbon_density/fuel.energy_density
        tax_per_mwh = fuels.carbon_tax.carbon_tax*carbon_per_mwh
        return tax_per_mwh
    

@dataclass
class StoragePlant:
    ''' Defines storage plants (pumped hydro and battery)
        Production and storage capacities are the amount that can be given/taken from the grid.
        reserve 

        maybe change current reserves to change each day idk.
    '''
    name: str
    technology: str
    company_name: str
    capacity: int
    production_capacity_MW_ratio: float
    storage_capacity_MW_ratio: float
    reserve_capacity_MWh_ratio: float
    gen_eff:float
    store_eff: float
    transmission_efficiency: float 

    company = None 
    current_reserves_MWh: float = None

    target_final_reserve_fraction = 0.5
    energy_supplied_per_hour: list = field(default_factory=lambda:[])

    # construction_length: int = 5
    # construction_start_date: int = 2023
    # construction_end_date: int = 2023
    # operational_length_years: float = 40
    # variable_costs_per_MWH: float = 100
    # fixed_costs_per_H: float = 10000
    # build_costs: float = 200000000
    # load_factor: float = 1.0
    # variable_maintenance_per_MWh: float = 5
    # is_operating: bool = False
    # interest_rate = 0.075
    # yearly_debt_payment = 0
    # npv = None
    # being_built = False

    def __post_init__(self):
        self.current_reserves_MWh_ratio = self.target_final_reserve_fraction*self.reserve_capacity_MWh_ratio
        self.set_storage_amount(self.capacity)

    def set_storage_amount(self, cap):
        self.capacity  = cap
        self.production_capacity_MW =cap*self.production_capacity_MW_ratio
        self.storage_capacity_MW = cap*self.storage_capacity_MW_ratio
        self.reserve_capacity_MWh = cap*self.reserve_capacity_MWh_ratio
        self.current_reserves_MWh = cap*self.current_reserves_MWh_ratio

    def get_days_production(self, predicted_prices):
        prices = tuple(predicted_prices)
        NH = len(predicted_prices)
        prod = Forecast.storage_production(
            NH = NH, 
            Emax = self.production_capacity_MW,
            Smax = self.storage_capacity_MW,
            prices = prices,
            h = self.transmission_efficiency,
            R0 = self.current_reserves_MWh,
            Rmax=self.reserve_capacity_MWh,
            eff_g=self.gen_eff,
            eff_st=self.store_eff, 
            f= self.target_final_reserve_fraction
        )

        return prod[:24]