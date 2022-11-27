import mesa


'''
agent that sets the demand. implement later. 
Daily demand, varies alot - yearly demand remains constant. 

just 1 day demand, per hour
Currently, list of average demands in MW


'''

# hourly_demand_MW = [20000, 20000, 20000, 20000, 
#         20000, 25000, 25000, 30000, 
#         30000, 40000, 40000, 40000, 
#         40000, 40000, 40000, 40000,
#         40000, 45000, 45000, 45000,
#         40000, 35000, 30000, 25000]


hourly_demand_MW = [15000, 30000, 20000]

class DemandAgent(mesa.Agent):
    def __init__(self, hourly_demand_MW: list):
        self.hourly_demand_MW = hourly_demand_MW

