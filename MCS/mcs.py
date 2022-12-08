import os
import sys
import optparse
from turtle import color, pos
from random import sample
import argparse
import random
from pandas import *


# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  # Checks for the binary in environ vars
import traci


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

#Sebességmérés
def avarageSpeed():

    detSpeed0 = traci.lanearea.getLastStepMeanSpeed("det_0")
    detSpeed1 = traci.lanearea.getLastStepMeanSpeed("det_1")
    occupancy_det0 = traci.lanearea.getLastStepOccupancy("det_0")
    occupancy_det1 = traci.lanearea.getLastStepOccupancy("det_1")

    if( occupancy_det0 == 100.0):
        return 0
    elif(occupancy_det1 == 100.0):
        return 0

    
    if( detSpeed0 == -1 or detSpeed1 ==-1):
        if(detSpeed0 == -1  and detSpeed1 != -1):
            return detSpeed1
        elif(detSpeed1 == -1 and detSpeed0!= -1):
            return detSpeed0
        else:
            return 36.11
    else:
        return ((detSpeed0+detSpeed1)/2)

#Él alapján történő sebességszabályozás - nincs használatban
def speedLimiter(thresold_high, threshold_low, base_speed, detectedSpeed):
    
    if( detectedSpeed >= thresold_high or detectedSpeed==-1):
        traci.edge.setMaxSpeed("e2",base_speed)
        traci.edge.setMaxSpeed("e3",base_speed)
        traci.edge.setMaxSpeed("e1",base_speed)
    elif( detectedSpeed < thresold_high and detectedSpeed >=threshold_low):
        traci.edge.setMaxSpeed("e2",thresold_high)
        traci.edge.setMaxSpeed("e3",thresold_high)
        traci.edge.setMaxSpeed("e1",base_speed)
    else:
        traci.edge.setMaxSpeed("e2",threshold_low)
        traci.edge.setMaxSpeed("e3",threshold_low)
        traci.edge.setMaxSpeed("e1",thresold_high)



    file1 = open(file,"r")
    lines = file1.readlines()
    file1.close()
    count = 0
    sum = 0

    for  line in lines:
        count +=1
        sum += float(line)
    
    avg = sum/count
    file2 = open("Eredmeny.txt","w")
    file2.write(str(avg))
    file2.close()

#Rövid statisztikák előkészítése
def makeStatistics( List_e0,List_e1,List_e2,List_e3,List_halted):

    if(traci.edge.getTraveltime("e0") >0):
        List_e0.append(traci.edge.getTraveltime("e0"))
    if(traci.edge.getTraveltime("e1") >0):
        List_e1.append(traci.edge.getTraveltime("e1"))
    if(traci.edge.getTraveltime("e2") >0):   
        List_e2.append(traci.edge.getTraveltime("e2"))
    if(traci.edge.getTraveltime("e3") >0):
        List_e3.append(traci.edge.getTraveltime("e3"))
    List_halted.append(traci.edge.getLastStepHaltingNumber("e0"))
    List_halted.append(traci.edge.getLastStepHaltingNumber("e1"))
    List_halted.append(traci.edge.getLastStepHaltingNumber("e2"))
    List_halted.append(traci.edge.getLastStepHaltingNumber("e3"))
    List_halted.append(traci.edge.getLastStepHaltingNumber("eEnd"))

#Rövid statisztikák készítése
def averageStatistics( List_e0,
                       List_e1,
                       List_e2,
                       List_e3,
                       HaltedNumber,
                       threshold_high,
                       threshold_low,
                       vehicle_rate,
                       alfa ):
    sum0 = 0
    sum1 = 0
    sum2 = 0
    sum3 = 0
    sumHalt = 0
    count0 = 0
    count1 = 0
    count2 = 0
    count3 = 0

    for item in List_e0:
        count0 +=1
        sum0 += item
    avg0 = sum0/count0
    for item in List_e1:
        count1 +=1
        sum1 += item
    avg1 = sum1/count1
    for item in List_e2:
        count2 +=1
        sum2 += item
    avg2 = sum2/count2    
    for item in List_e3:
        count3 +=1
        sum3 += item
    avg3 = sum3/count3
    for item in HaltedNumber:
        sumHalt += item

    avgTotal = (avg0 + avg1 + avg2 + avg3)/4

    file = open("Statistics.txt","a")
    file.write("Travel Time Statistics With Parameters:\n")
    file.write("Threshold high: " + str(threshold_high) + " -  Threshold low: " + str(threshold_low) + " - Controlled Vehicle Rate: " + str(vehicle_rate)+ " Alfa: " + str(alfa) +"\n")
    file.write("e0: "+ str(avg0)+ "\n")
    file.write("e1: "+ str(avg1)+ "\n")
    file.write("e2: "+ str(avg2)+ "\n")
    file.write("e3: "+ str(avg3)+ "\n\n")
    file.write("Total: "+ str(avgTotal)+ "\n\n")
    file.write("TotalHaltedNumber: "+ str(sumHalt)+ "\n\n")

    file.close()

#A módosított autók kiválasztása
def vehicleSelector(speed,edge,rate,last_vehicles):

    list = traci.edge.getLastStepVehicleIDs(edge)
    number = 0
    controlled=0
    for vehicle in list:

        if( vehicle not in last_vehicles):
            number +=1
            n = random.randrange(1,11,1)
            if( (10*rate)>=n ):
                 controlled +=1
                 traci.vehicle.setSpeed(vehicle,speed)
                 traci.vehicle.setColor(vehicle,(255,0,0))
    
    print("Ennyit állít át:" + str(controlled) +" " + str(number) +"-bol")       
    return list

#A sebesség ajánlást lekezelő metódus
def edgeSpeedController(thresold_high, threshold_low, rate,
    speed_before,alfa,vehicle_list_e3,vehicle_list_e2):

    detectedSpeed = avarageSpeed()
    print(detectedSpeed)
    measuredSpeed = alfa * detectedSpeed + (1-alfa)*speed_before
    if( detectedSpeed < thresold_high 
        and detectedSpeed >=threshold_low):

        vehicle_list_e3=vehicleSelector(thresold_high,"e3",rate,vehicle_list_e3)

    elif( detectedSpeed < thresold_high 
        and detectedSpeed <threshold_low):

        vehicle_list_e3=vehicleSelector(threshold_low,"e3",rate,vehicle_list_e3)
        vehicle_list_e2=vehicleSelector(thresold_high,"e2",rate,vehicle_list_e2)

    return (measuredSpeed,vehicle_list_e3,vehicle_list_e2)

def toFileTripinfo(number):

    destination = open("Test-Tripinfo" + str(number) + ".xml", "w")
    source = open("tripinfo.xml", "r")
    destination.write(source.read())
    source.close()
    destination.close()

# contains TraCI control loop
def run(threshold_high, threshold_low, rate, alpha,number):
    
    MeasuredSpeed = 36.11
    step = 0
    List_vehicles_e3 = []
    List_vehicles_e2 = []


    #Az első megálló autó
    traci.vehicle.setStop(vehID="0",edgeID="e3",duration="1000", pos="500")
    
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
     
        #Sebességajánlás
        modified_params = edgeSpeedController(threshold_high,
            threshold_low,rate,MeasuredSpeed,alpha,
            List_vehicles_e3,List_vehicles_e2)
        MeasuredSpeed = modified_params[0]
        List_vehicles_e3 = modified_params[1]
        List_vehicles_e2 = modified_params[2]
        if(step==2500):
            #A második megálló autó
            traci.vehicle.setStop(vehID="1",edgeID="e3",
            duration="3000", pos="1000")
        if(step==7500):
        #A második megálló autó
            traci.vehicle.setStop(vehID="2",edgeID="e3",
            duration="1000", pos="1000")
        if(step==9000):
            #A második megálló autó
            traci.vehicle.setStop(vehID="3",edgeID="e3",
            duration="2000", pos="1000")
        if(step==11500):
            #A második megálló autó
            traci.vehicle.setStop(vehID="4",edgeID="e3",
            duration="500", pos="1000")
        
        step += 1

    traci.close()
    toFileTripinfo(number)
    toFile(number)
    sys.stdout.flush()


#Az argparse-szal beolvasott paramétereket formalizálja
def paramsFromLines(args):

    Lines = args.filename.readlines()

    parameterList = []
    
    for line in Lines:
        parameters = line.split()
        new_list = []
        new_list.append(float(parameters[0]))
        new_list.append(float(parameters[1]))
        new_list.append(float(parameters[2]))
        new_list.append(float(parameters[3]))
        parameterList.append(new_list)
    
    return parameterList

def toFile(number):

    destination = open("Test-" + str(number) + ".xml","w")
    source = open("det.out.xml","r")
    destination.write(source.read())
    source.close()
    destination.close()




# main entry point
if __name__ == "__main__":

    options = get_options()

    #argparser for the input variables

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    #reading input from the given file with argparse

    data = read_csv("input.csv")

    threshold_high = data["Threshold_high"].tolist()
    threshold_low = data["Threshold_low"].tolist()
    rate = data["Rate"].tolist()
    alpha = data["Alpha"].tolist()
    number = 0
    #A szimmuláció az input fájlban megadott paraméteregyüttesek száma alapján fut le

    for i in range(len(rate)):

        traci.start([sumoBinary, "-c", "mcs.sumocfg",
                             "--start",
                             "--quit-on-end",
                             "--tripinfo-output", "tripinfo.xml"])

        run(threshold_high[i],threshold_low[i],rate[i],alpha[i],number)
        number += 1
   

    