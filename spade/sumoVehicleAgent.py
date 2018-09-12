# -*- coding: utf-8 -*-

# sumo imports
from __future__ import absolute_import
from __future__ import print_function
import subprocess
import random
import sys
import getopt
import os
from optparse import OptionParser

# spade imports
import spade
import time
import ast

host = "127.0.0.1"
file = open('log.txt', 'a')
sys.stdout = file

"""
Agente que representa um veículo.
"""
class VehicleAgent(spade.Agent.Agent):

    """
    Construtor
    """
    def __init__(self, ip, _pass, origin, destination, debug):
        spade.Agent.Agent.__init__(self, ip, _pass)
        self.debug  = debug
        self.origin = origin
        self.destination = destination
        self.neighbours = []
        self.nb_pref    = {}
        self.change_direction = True if origin != destination else False
        self.norm_right = False
        self.rightOfWay = False

        self.vehicle_ID          = None
        self.vehicle_angle       = None
        self.vehicle_signals     = None
        self.vehicle_left_blink  = None
        self.vehicle_right_blink = None
        self.vehicle_state       = ""

    def _setup(self):

        self.STATE_ZERO_CODE  = 0
        self.STATE_ONE_CODE   = 1
        self.STATE_TWO_CODE   = 2
        self.STATE_THREE_CODE = 3
        self.STATE_FOUR_CODE  = 4
        self.STATE_FIVE_CODE  = 5
        self.STATE_SIX_CODE   = 6
        self.STATE_SEVEN_CODE = 7

        self.TRANSITION_TO_ZERO  = 00
        self.TRANSITION_TO_ONE   = 10
        self.TRANSITION_TO_TWO   = 20
        self.TRANSITION_TO_THREE = 30
        self.TRANSITION_TO_FOUR  = 40
        self.TRANSITION_TO_FIVE  = 50
        self.TRANSITION_TO_SIX   = 60
        self.TRANSITION_TO_SEVEN = 70
        self.TRANSITION_DEFAULT  = 1000

        fsm = spade.Behaviour.FSMBehaviour()

        fsm.registerFirstState(self.StartBehaviour(),   self.STATE_ZERO_CODE)
        fsm.registerState(self.ArriveBehaviour(),       self.STATE_ONE_CODE)
        fsm.registerState(self.HelloBehaviour(),        self.STATE_TWO_CODE)
        fsm.registerState(self.WaitBehaviour(),         self.STATE_THREE_CODE)
        fsm.registerState(self.DecideBehaviour(),       self.STATE_FOUR_CODE)
        fsm.registerState(self.DecideToStayBehaviour(), self.STATE_FIVE_CODE)
        fsm.registerState(self.DecideToGoBehaviour(),   self.STATE_SIX_CODE)
        fsm.registerLastState(self.GoneBehaviour(),     self.STATE_SEVEN_CODE)

        fsm.registerTransition(self.STATE_ZERO_CODE,  self.STATE_ZERO_CODE,  self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_ZERO_CODE,  self.STATE_ZERO_CODE,  self.TRANSITION_TO_ZERO)
        fsm.registerTransition(self.STATE_ZERO_CODE,  self.STATE_ONE_CODE,   self.TRANSITION_TO_ONE)

        fsm.registerTransition(self.STATE_ONE_CODE,   self.STATE_ONE_CODE,   self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_ONE_CODE,   self.STATE_TWO_CODE,   self.TRANSITION_TO_TWO)

        fsm.registerTransition(self.STATE_TWO_CODE,   self.STATE_TWO_CODE,   self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_TWO_CODE,   self.STATE_THREE_CODE, self.TRANSITION_TO_THREE)

        fsm.registerTransition(self.STATE_THREE_CODE, self.STATE_THREE_CODE, self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_THREE_CODE, self.STATE_FOUR_CODE,  self.TRANSITION_TO_FOUR)

        fsm.registerTransition(self.STATE_FOUR_CODE,  self.STATE_FOUR_CODE,  self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_FOUR_CODE,  self.STATE_FIVE_CODE,  self.TRANSITION_TO_FIVE)
        fsm.registerTransition(self.STATE_FOUR_CODE,  self.STATE_SIX_CODE,   self.TRANSITION_TO_SIX)

        fsm.registerTransition(self.STATE_FIVE_CODE,  self.STATE_FIVE_CODE,  self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_FIVE_CODE,  self.STATE_TWO_CODE,   self.TRANSITION_TO_TWO)

        fsm.registerTransition(self.STATE_SIX_CODE,   self.STATE_SIX_CODE,   self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_SIX_CODE,   self.STATE_SEVEN_CODE, self.TRANSITION_TO_SEVEN)

        self.addBehaviour(fsm, None)

        template = spade.Behaviour.ACLTemplate()
        # template.setSender(spade.AID.aid("car1@" + host, ["xmpp://car1@" + host]))
        template.setOntology("Car2X")
        template.setProtocol("WAVE")
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(self.RecvMsgBehaviour(), t)


    def getVehicleState(self):
        return self.vehicle_state

    """
    Coleta dados do SUMO para auxiliar o mecanismo de decisão do agente.
    """
    def collectSumoData(self, vehID, data):

        self.vehicle_ID    = vehID
        self.vehicle_angle = round(data[tc.VAR_ANGLE], 2)

        self.vehicle_signals = '{:013b}'.format(data[tc.VAR_SIGNALS])  # Got vehicle signals from http://sumo.dlr.de/wiki/TraCI/Vehicle_Signalling

        self.vehicle_right_blink = bool(int(self.vehicle_signals[12]))
        self.vehicle_left_blink  = bool(int(self.vehicle_signals[11]))

    """
    Adiciona vizinhos para envio de mensagens.
    """
    def addNeighbour(self, neighbour):
        self.neighbours.append(neighbour)

    """
    Verifica se posição de vizinho está à direita.
    """
    def checkRightSide(self, direction):

        self.carAtRight = None

        if self.origin == direction:
            self.carAtRight = False
        else:
            if self.origin == "NORTH":
                self.carAtRight = True if direction == "WEST" else False
            elif self.origin == "SOUTH":
                self.carAtRight = True if direction == "EAST" else False
            elif self.origin == "WEST":
                self.carAtRight = True if direction == "SOUTH" else False
            elif self.origin == "EAST":
                self.carAtRight = True if direction == "NORTH" else False

        return self.carAtRight

    """
    Verifica se o vizinho vai mudar de direção
    """
    def checkChangeDirection(self, origin, destination):

        if origin != destionation:
            return True
        else:
            return False

    """
    Prepara mensagem a ser enviada por agente.
    """
    def prepareMessage(self, status):
        self.msg = spade.ACLMessage.ACLMessage()
        self.msg.setPerformative("inform")
        self.msg.setLanguage("OWL-S")
        self.msg.setOntology("Car2X")
        self.msg.setProtocol("WAVE")
        self.content = "{'status':'"+ status + "','from':'" + self.origin + "','to':'" + self.destination + "'}"
        self.msg.setContent(self.content)

        return self.msg

    def removeNeighbour(self, neighbour):
        self.neighbours.pop(neighbour)

    """
    Comportamento de recebimento de mensagens.
    """
    class RecvMsgBehaviour(spade.Behaviour.EventBehaviour):

        def _process(self):
            msg = self._receive(True, None)

            self.content = ast.literal_eval(msg.getContent())
            self.status  = self.content['status']
            self.origin  = self.content['from']
            self.dest    = self.content['to']

            if msg.getSender() in self.myAgent.neighbours:

                if   self.status == "COMING":
                    self.myAgent.rightOfWay = False
                    self.myAgent.nb_pref[msg.getSender().getName()] = False
                    # print(str(self.myAgent.getName()) + "| Got message COMING from " + msg.getSender().getName() + ". It is crossing now.")

                elif self.status == "WAITING":

                    self.right_position   = self.myAgent.checkRightSide(self.origin)
                    self.change_direction = self.origin != self.dest

                    # Trata vizinhos que estiverem à direita
                    if not self.right_position:
                        self.myAgent.nb_pref[msg.getSender().getName()] = True
                    else:
                        self.myAgent.nb_pref[msg.getSender().getName()] = True if self.change_direction else False

                    # print(str(self.myAgent.getName()) + "| Got message WAITING from " + msg.getSender().getName() + ". My right-of-way compared to it is " + self.myAgent.nb_pref[msg.getSender().getName()] + ".")

                else: # self.status == "GONE"
                    self.myAgent.nb_pref.pop(msg.getSender().getName())
                    # print(str(self.myAgent.getName()) + "| Got message GONE from " + msg.getSender().getName() + ". It has gone.")

                if bool(self.myAgent.nb_pref):
                    if self.myAgent.change_direction:
                        self.myAgent.rightOfWay = False
                        # print(str(self.myAgent.getName()) + "| I'm about to make a turn and other car(s) have right-of-way.")
                    else:
                        self.myAgent.rightOfWay = False if False in self.myAgent.nb_pref.values() else True
                        # print(str(self.myAgent.getName()) + "| I have right-of-way.")
                else:
                    self.myAgent.rightOfWay = True
                    # print(str(self.myAgent.getName()) + "| I'm about to make a turn and I have right-of-way.")

                # if self.myAgent.debug:
                    # print str(self.myAgent.getName()) + "| Messagem from " + str(msg.getSender().getName()) + ". Status " + self.status + " Origin " + self.origin + ". Right of way is " + str(self.right) + ". General right of way is " + str(self.myAgent.rightOfWay) + "."
                    # print self.myAgent.nb_pref

    """
    Comportamento de criação de veículo no SUMO
    """
    class StartBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "start"
            if self.myAgent.vehicle_ID != None:
                if self.myAgent.debug:
                    print (str(self.myAgent.getName()) + "| Starting Behaviours.")
                # file.flush()
                    self._exitcode = self.myAgent.TRANSITION_TO_ONE
            else:
                self._exitcode = self.myAgent.TRANSITION_TO_ZERO

    """
    Comportamento de chegada de veículos ao cruzamento.
    """
    class ArriveBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "arrive"
            if self.myAgent.debug:
                print (str(self.myAgent.getName()) + "| Arriving at crossing.")

            time.sleep(1)
            self._exitcode = self.myAgent.TRANSITION_TO_TWO

    """
    Comportamento que envia mensagem de interesse em atravessar o cruzamento.
    """
    class HelloBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "hello"
            if self.myAgent.debug:
                print (str(self.myAgent.getName()) + "| Sending message.")
                # file.flush()

            ######## send Message "Waiting" ########
            self.msg = self.myAgent.prepareMessage("WAITING")
            for receiver in self.myAgent.neighbours:
                self.msg.addReceiver(receiver)
            self.myAgent.send(self.msg)
            #######################################
            time.sleep(1)
            self._exitcode = self.myAgent.TRANSITION_TO_THREE

    """
    Comportamento que aguarda mensagens de outros agentes carros.
    """
    class WaitBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "wait"
            if self.myAgent.debug:
                print (str(self.myAgent.getName()) + "| Waiting.")
                # file.flush()

            time.sleep(1)
            # print str(self.myAgent.getName()) + "| Waiting time is over."
            self._exitcode = self.myAgent.TRANSITION_TO_FOUR


    """
    Comportamento que contém o mecanismo de decisão que pode escolher (aguardar
    ou atravessar) baseando-se nas normas e nas mensagens recebidas.
    """
    class DecideBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "decide"
            if self.myAgent.debug:
                print(str(self.myAgent.getName()) + "| Deciding.")
                # file.flush()
            time.sleep(3)
            # if permission_to_go && norms_checked


            if self.myAgent.rightOfWay :
                self._exitcode = self.myAgent.TRANSITION_TO_SIX
            else:
                self._exitcode = self.myAgent.TRANSITION_TO_FIVE

    """
    Comportamento que dispara mensagem e espera para atravessar.
    """
    class DecideToStayBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "stay"
            if self.myAgent.debug:
                print(str(self.myAgent.getName()) + "| Staying.")

            time.sleep(1)
            # if self.myAgent.getName() == "car1@127.0.0.1":
            self.myAgent.permission_to_go = True
            self._exitcode = self.myAgent.TRANSITION_TO_TWO

    """
    Comportamento que dispara mensagem e atravessa o cruzamento.
    """
    class DecideToGoBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "go"
            if self.myAgent.debug:
                print (str(self.myAgent.getName()) + "| Coming.")

            ######## send Message "Coming" ########
            self.msg = self.myAgent.prepareMessage("COMING")
            for receiver in self.myAgent.neighbours:
                self.msg.addReceiver(receiver)
            self.myAgent.send(self.msg)
            #######################################
            time.sleep(2)
            self._exitcode = self.myAgent.TRANSITION_TO_SEVEN

    """
    Comportamento que dispara mensagem e conclui a travessia do cruzamento.
    """
    class GoneBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            self.myAgent.vehicle_state = "gone"
            if self.myAgent.debug:
                print(str(self.myAgent.getName()) + "| Crossing complete.")
                # file.flush()

            ######## send Message "Gone" ##########
            self.msg = self.myAgent.prepareMessage("GONE")
            for receiver in self.myAgent.neighbours:
                self.msg.addReceiver(receiver)
            self.myAgent.send(self.msg)
            #######################################

            time.sleep(3)
            self._exitcode = self.myAgent.TRANSITION_TO_DEFAULT
            self.myAgent._kill()


try:     # we need to import python modules from the $SUMO_HOME/tools directory
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


def runSumo():

    sumoBinary = "/home/lauro/Documentos/Mestrado/T3/sumo/sumo-0.32.0/bin/sumo-gui"
    sumoCmd = [sumoBinary, "-c", "../sumo/cross.sumocfg"]

    # SUMO Magic
    traci.start(sumoCmd)
    junctionID = "0"
    traci.junction.subscribeContext(junctionID, tc.CMD_GET_VEHICLE_VARIABLE, 15, [tc.VAR_SPEED, tc.VAR_ANGLE, tc.VAR_SIGNALS, tc.VAR_EDGES])

    # for step in range(100):
    while traci.simulation.getMinExpectedNumber() > 0:
       # print(step)
       traci.simulationStep()
       data = traci.junction.getContextSubscriptionResults(junctionID)

       if str(type(data)) == "<type 'dict'>":
           for car in data:
               agent = agents[car]
               agent.collectSumoData(car, data[car])


               if agent.getVehicleState() == "start":
                   traci.vehicle.setSpeed(car, 0)
               elif agent.getVehicleState() == "wait":
                   traci.vehicle.setSpeed(car, 0)
               elif agent.getVehicleState() == "go":
                   traci.vehicle.setSpeed(car, -1)

    file.close()
    traci.close()


if __name__== "__main__":

# As normas em cruzamento de veículos sempre acabam dependendo da sinalização (vertical/horizontal) para auxiliar a tomada de decisão no trânsito.
# Para 3 carros
#   A norma da preferência de quem estiver a direita resolve a definição de prioridade.
# Para 2 carros
#   A norma da preferência a direita resolve a definição de prioridade em 4 dos 6 casos.
#   Para os carros em paralelo, pode-se usar a norma da mudança de direção. (o que muda de direção perde a prioridade)
#   Para os carros em paralelo, não é necessário usar norma de prioridade se ambos estão em faixas diferentes e vão para direções opostas.
#   Para carros em paralelo mudando de direção para o mesmo destino, não sei como priorizar.
# Para 4 carros


    # Caso Base
# Preferencia red, pink, yellow
   red    = VehicleAgent("red"    + "@" + host, "secret", "EAST",  "NORTH", True)
   pink   = VehicleAgent("pink"   + "@" + host, "secret", "WEST",  "WEST",  True)
   yellow = VehicleAgent("yellow" + "@" + host, "secret", "SOUTH", "SOUTH", True)

# Preferencia pink, yellow, red
   # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
   # yellow = VehicleAgent("yellow@" + host, "secret", "NORTH", "NORTH", True)
   # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)

# Preferencia red, yellow, pink
   # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
   # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
   # yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)

    # Collecting values from simulation models to feed agent decision mechanism
   agents = {"red":red, "pink":pink, "yellow":yellow}

   red.addNeighbour(pink.getAID())
   red.addNeighbour(yellow.getAID())

   pink.addNeighbour(red.getAID())
   pink.addNeighbour(yellow.getAID())

   yellow.addNeighbour(red.getAID())
   yellow.addNeighbour(pink.getAID())

   red.start()
   pink.start()
   yellow.start()

   # red.wui.start()
   # pink.wui.start()
   # yellow.wui.start()

   # red.setDebugToScreen()
   # pink.setDebugToScreen()
   # yellow.setDebugToScreen()

   runSumo()
