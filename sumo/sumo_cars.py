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

sumoBinary = "/home/lauro/Documentos/Mestrado/T3/sumo/sumo-0.32.0/bin/sumo-gui"
sumoCmd = [sumoBinary, "-c", "cross.sumocfg"]

traci.start(sumoCmd)
# step = 0

# vehID = "left_0"
# traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION, tc.VAR_ANGLE))

junctionID = "0"
agents = []
traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 15, [tc.VAR_SPEED, tc.VAR_ANGLE, tc.VAR_SIGNALS, tc.VAR_EDGES])
print(traci.junction.getContextSubscriptionResults(junctionID))

for step in range(1000):
   print("step", step)
   traci.simulationStep()

   data = traci.junction.getContextSubscriptionResults(junctionID)

   # python3 :
   # if type(data) is dict:

   if str(type(data)) == "<type 'dict'>":
       for car in data:
           if car not in agents:
               print("Adicionado carro " + car + " à simulação")
               agents.append(car)
           else:
              print(car + " | " + str(data[car][tc.VAR_SIGNALS]))





   # if type(data) != 'NoneType':
       # print(data.get(tc.CMD_GET_VEHICLE_VARIABLE))

   # print(type(data))

# while step < 1000:
#     traci.simulationStep()
#     step += 1

    # print(str(step) + " : " + str(traci.vehicle.getSubscriptionResults(vehID)))

traci.close()
