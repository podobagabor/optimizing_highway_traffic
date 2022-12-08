import os
import sys
import optparse
import random
from turtle import color, pos
from pandas import *

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


from sumolib import checkBinary  
import traci


def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                          default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options

# A módosított autók kiválasztása


def vehicleSelector(speed, edge, rate, last_vehicles):
    list = traci.edge.getLastStepVehicleIDs(edge)
    for vehicle in list:

        if (vehicle not in last_vehicles):
            number += 1
            n = random.randrange(1, 11, 1)
            if ((10*rate) >= n):
                controlled += 1
                traci.vehicle.setSpeed(vehicle, speed)
    return list

def getDetectedFlow():
    sumOfVehicles = traci.inductionloop.getLastStepVehicleNumber(
        "det_0") + traci.inductionloop.getLastStepVehicleNumber("det_1")
    return sumOfVehicles


def refreshSpeed(edge):
    for id in traci.edge.getLastStepVehicleIDs(edge):
        if (traci.vehicle.getTypeID(id) == "normal_car" or traci.vehicle.getTypeID(id) == "sportly_car"):
            traci.vehicle.setSpeed(id, 36.11)
        if (traci.vehicle.getTypeID(id) == "bus"):
            traci.vehicle.setSpeed(id, 27.78)
        if (traci.vehicle.getTypeID(id) == "truck"):
            traci.vehicle.setSpeed(id, 26.4)


def toFile(number):

    destination = open("Test-" + str(number) + ".xml", "w")
    source = open("det.out.xml", "r")
    destination.write(source.read())
    source.close()
    destination.close()


def toFileTripinfo(number):

    destination = open("Test-Tripinfo" + str(number) + ".xml", "w")
    source = open("tripinfo.xml", "r")
    destination.write(source.read())
    source.close()
    destination.close()

# contains TraCI control loop


def run(maxCapacity, reducedSpeed, alpha, rate, reducedSpeedInflow,number,):
    step = 0
    vehicleList = []
    vehicleListInflow = []
    flow_value = 0
    controller_is_active = False
    previousFlowValue = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        flow_value += getDetectedFlow()
        if (step % 60 == 0):
            flowSum = (flow_value * 60 *alpha ) + (( 1 - alpha) * previousFlowValue)
            previousFlowValue = flowSum
            if (flowSum > maxCapacity * 2):
                controller_is_active = True
            else:
                controller_is_active = False
            flow_value = 0
        if (controller_is_active): 
            vehicleList = vehicleSelector(
                reducedSpeed, "eSpeedControlled", rate, vehicleList)
            vehicleListInflow = vehicleSelector(
                reducedSpeedInflow, "eInflow", rate, vehicleListInflow)
            
        refreshSpeed("eBottleneck")
        step += 1

    traci.close()
    toFile(number)
    toFileTripinfo(number)
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    data = read_csv("input.csv")

    maxCapacity = data["MaxCapacity"].tolist()
    Speed = data["Speed"].tolist()
    Alpha = data["Alpha"].tolist()
    Rate = data["Rate"].tolist()
    ReducedSpeedInflow = data["ReducedSpeedInflow"].tolist()
    number = 0

    # traci starts sumo as a subprocess and then this script connects and runs
    for i in range(len(Rate)):

        traci.start([sumoBinary, "-c", "mtfc.sumocfg", "--start", "--tripinfo-output", "tripinfo.xml",
                     "--quit-on-end"])
        run(maxCapacity[i], Speed[i], Alpha[i], Rate[i],ReducedSpeedInflow[i], number)
        number += 1
