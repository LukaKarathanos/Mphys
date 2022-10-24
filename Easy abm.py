import numpy as np
from matplotlib import pyplot as plt
import random
import pycxsimulator
    
n = 1000 # number of agents
r = 0.35 # neighbourhood radius
th = 0.5 #threshold for moving 


class agent():
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y

def initialise():
    global agents
    agents = []
    for i in range(n):
        type = random.randint(0,1)
        x = random.random()
        y = random.random()
        agents.append(agent(type, x, y))

def observe():
    global agents
    plt.cla()
    poor = [ag for ag in agents if ag.type == 0]
    rich = [ag for ag in agents if ag.type == 1]
    plt.plot([ag.x for ag in poor], [ag.y for ag in poor], 'r.')
    plt.plot([ag.x for ag in rich], [ag.y for ag in rich], 'b.')
    plt.axis('image')
    plt.axis([0,1,0,1])


nb = 0 #number of updates
def update():   
    global agents
    global nb
    ag = agents[random.randint(0,n-1)]
    neighbours = [nb for nb in agents if  (ag.x - nb.x)**2 + (ag.y - nb.x)**2 < r**2 and nb != ag]
    nb += 1
    if nb % 1000 == 0:
        print(f'{nb} updates')

    if len(neighbours) > 0:
        q = len([nb for nb in neighbours if nb.type == ag.type])/len(neighbours)
        if  q <= th: 
            ag.x, ag.y = random.random(), random.random()   
            print(f'Moved to {ag.x}, {ag.y}')     


''' Visualising using pyxcsimulator '''
pycxsimulator.GUI().start(func=[initialise, observe, update])



