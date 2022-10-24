import matplotlib as mpl
import matplotlib.pyplot as plotter
import matplotlib.animation as anim
import numpy
import Person as person


class Canvas:
    def __init__(self,People,Nsteps):
        self.people  = People
        self.dim     = self.people.Dim()
        self.people.SetCanvas(self)
        self.InitLines()
        self.statuslist = []
        self.Harvest()

    def InitLines(self):
        self.S = []
        self.I = []
        self.R = []
        self.D = []
        
    def Harvest(self):
        for x in range(self.dim):
            statusrow = []
            for y in range(self.dim):
                statusrow.append(self.people.Get(x,y).Colour())
            self.statuslist.append(statusrow)
            
    def Update(self,step):
        fig,axs = plotter.subplots(2)
        fig.suptitle(r"A Simple Simulation $\beta=0.5$, $\mu=0.07$, and $R_D=5\%$")
        showed  = axs[0]
        summary = axs[1]
        showed.axis([-0.5,self.dim-0.5,-0.5,self.dim-0.5])
        showed.matshow(self.statuslist)        

        self.S.append(self.people.NHealthy()*100.)
        self.I.append(self.people.NInfected()*100.)
        self.R.append(self.people.NImmune()*100.)
        self.D.append(self.people.NDead()*100.)
        summary.set_xlim(0,100)
        summary.plot(self.S,label="Susceptible",color='green',marker=".",linestyle="None")
        summary.plot(self.I,label="Infected",color='red',marker=".",linestyle="None")
        summary.plot(self.R,label="Recovered",color='blue',marker=".",linestyle="None")
        summary.plot(self.D,label="Dead",color='black',marker="+",linestyle="None")
        summary.legend(loc="center left")
        summary.set_ylim(0.,110)
        summary.grid()
        summary.set_ylabel("Proportion of Population [%]")
        summary.set_xlabel("Time [Days]")
        filename = "Sim"+"{:03d}".format(step)+".png"
        plotter.savefig(filename)
        if step==99:
            for i in range(50):
                filename = "Sim"+"{:03d}".format(step+i)+".png"
                plotter.savefig(filename)
        plotter.close()
        
        
    def GetList(self):
        return self.statuslist

    def Print(self):
        print (self.statuslist)
    
if __name__ == "__main__":
    dim     = 200
    Nsteps  = 100

    people  = person.People(dim)
    canvas  = Canvas(people,Nsteps)
    illness = person.Illness(people,canvas)

    people.Seed(illness,3)
    people.Evolution(Nsteps,illness)
    
