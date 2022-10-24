import matplotlib as mpl
import matplotlib.pyplot as plotter
import matplotlib.animation as anim
import numpy

def update(S,I,R,D,N,beta,muR,RD):
    Snew = S[-1] - beta * S[-1]*I[-1] / 100
    Inew = I[-1] + beta * S[-1]*I[-1] / 100 - muR*I[-1]
    Dnew = D[-1] + muR*I[-1] * RD
    Rnew = 100. - Snew - Inew - Dnew
    S.append(Snew)
    I.append(Inew)
    R.append(Rnew)
    D.append(Dnew)

def plot(S,I,R,D,Nsteps,counter):
    fig,ax = plotter.subplots()
    ax.plot(S,label="Susceptible",color='green',marker=".",linestyle="None")
    ax.plot(I,label="Infected",color='red',marker=".",linestyle="None")
    ax.plot(R,label="Recovered",color='blue',marker=".",linestyle="None")
    ax.plot(D,label="Dead",color='black',marker="+",linestyle="None")
    ax.set_xlim(0,Nsteps)
    ax.set_xlabel("Time [days]")
    ax.set_ylabel("Proportion of Population [%]")
    ax.legend(loc="upper center")
    ax.set_title(r"SIR model with $\beta=0.3$, $\mu=0.07$, and $R_D=2\%$")
    #plotter.show(block=False)
    #plotter.pause(1)
    filename = "SIRpics/SIR"+"{:03d}".format(counter)+".png"
    plotter.savefig(filename)
    plotter.close()
    
if __name__ == "__main__":
    N       = 1000000
    Nsteps  = 100
    Istart  = 100
    beta    = 0.3
    muR     = 0.07
    RD      = 0.02

    S = [(N-Istart)/N*100]
    I = [Istart/N*100]
    R = [0]
    D = [0]

    plot(S,I,R,D,Nsteps,0)
    for i in range(1,Nsteps+1):
        update(S,I,R,D,N,beta,muR,RD)
        plot(S,I,R,D,Nsteps,i)
    for i in range(Nsteps+1,Nsteps+101):
        plot(S,I,R,D,Nsteps,i)
