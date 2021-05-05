import numpy as np
import matplotlib.pyplot as plt
import math



def ticks2dist(ticks):
    motor_rotations_per_meter=587.649
    ticks_per_wh_rev=20
    wheel_radius=.0325 #m
    ticks_per_meter=ticks_per_wh_rev/(2*math.pi*wheel_radius)# ticks/meter
    dist=100*ticks/ticks_per_meter
    print(dist*100)
    return dist # centimeters

def plotPath(start_pos, dist, ax):

    startx=start_pos[0]
    starty=start_pos[1]
    theta=np.deg2rad(start_pos[2])
    print(start_pos)
    # Assume ticks were counted while moving

    # convert ticks to distance
    #dist=ticks2dist(ticks)


    new_pos=[0,0,0]

    new_pos[0]=startx+dist*math.cos(theta)
    new_pos[1]=starty+dist*math.sin(theta)
    new_pos[2]=np.rad2deg(theta)

    # plot line from start_pos to end_pos
    x=np.linspace(startx,new_pos[0],500)
    y=np.linspace(starty,new_pos[1],500)


    ax.plot(x,y,'-')
    return new_pos


def startPlotting():
    fileName = "map_info.txt"

    fig,ax=plt.subplots()

    x = 0
    y = 0

    #count = 0
    angle = 0
    distance = 0
    pos = [x, y, 0]
    with open(fileName) as file:
        content = file.readlines()
        for line in content:
            separtateValues = line.split(",")
            currangle = float(separtateValues[0])
            distance = float(separtateValues[1])
            #if count == 0:
            #   angle = currangle
            #   print('starting pos')
            # if distance == float(0):
            #   angle = currangle - angle
            #   if angle < 0:
            #       angle = -(angle + 360)
            #   pos[2] += angle
            #if distance > 0:
            #else:
            pos[2] = currangle
            pos = plotPath(pos, distance, ax)
            #count += 1
        plt.grid()
        plt.xlabel('X Position (cm)')
        plt.ylabel('Y Position (cm)')
        plt.title("Robot Trajectory")
        plt.savefig('TrajectoryMap.jpg')
        print('[INFO] Map generated sucessfully!')
        #plt.show()