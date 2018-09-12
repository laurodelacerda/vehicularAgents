# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
import subprocess
import random
import sys
import os
from optparse import OptionParser

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary  # noqa
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci
import traci.constants as tc
from vehicleAgent import VehicleAgent


sumoBinary = "/home/lauro/Documentos/Mestrado/T3/sumo/sumo-0.32.0/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "../sumo/cross.sumocfg"]

host = "127.0.0.1"
vehicle = None

if __name__== "__main__":

    traci.start(sumoCmd)
# step = 0

# vehID = "left_0"
# traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_ANGLE))

    junctionID = "0"
    agents = []
    traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 15, [tc.VAR_SIGNALS])

    waiting = []
    preference = None
    onCorner = None


    for step in range(1000):

       traci.simulationStep()

       data = traci.junction.getContextSubscriptionResults(junctionID)

       if str(type(data)) == "<type 'dict'>":

           for car in data:

               for command in data[car]:
                   turnLeft = data[car][command]

                   if turnLeft == 10 :

                       print(traci.vehicle.getRoadID(car))

                       if car != preference:
                           preference = car
                           traci.vehicle.setSpeedMode(car, 23)
                           traci.vehicle.setSpeed(car, -1)

                   else: # other vehicles must stop
                       if car not in waiting and car!=preference:
                           waiting.append(car)
                           traci.vehicle.setSpeed(car, 0)
                       elif car == preference and onCorner!= None and onCorner != traci.vehicle.getRoadID(car):
                           for otherCar in waiting:
                                traci.vehicle.setSpeed(otherCar, -1)

                   if car == preference and traci.vehicle.getRoadID(preference) == ":0_4":
                       onCorner = traci.vehicle.getRoadID(car)

    traci.close()
