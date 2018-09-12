# -*- coding: utf-8 -*-
import spade
import time
import ast

host = "127.0.0.1"

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

    def _setup(self):

        self.STATE_ZERO_CODE  = 0
        self.STATE_ONE_CODE   = 1
        self.STATE_TWO_CODE   = 2
        self.STATE_THREE_CODE = 3
        self.STATE_FOUR_CODE  = 4
        self.STATE_FIVE_CODE  = 5
        self.STATE_SIX_CODE   = 6

        self.TRANSITION_TO_ZERO  = 00
        self.TRANSITION_TO_ONE   = 10
        self.TRANSITION_TO_TWO   = 20
        self.TRANSITION_TO_THREE = 30
        self.TRANSITION_TO_FOUR  = 40
        self.TRANSITION_TO_FIVE  = 50
        self.TRANSITION_TO_SIX   = 60
        self.TRANSITION_DEFAULT  = 1000

        fsm = spade.Behaviour.FSMBehaviour()
        fsm.registerFirstState(self.ArriveBehaviour(),  self.STATE_ZERO_CODE)
        fsm.registerState(self.HelloBehaviour(),        self.STATE_ONE_CODE)
        fsm.registerState(self.WaitBehaviour(),         self.STATE_TWO_CODE)
        fsm.registerState(self.DecideBehaviour(),       self.STATE_THREE_CODE)
        fsm.registerState(self.DecideToStayBehaviour(), self.STATE_FOUR_CODE)
        fsm.registerState(self.DecideToGoBehaviour(),   self.STATE_FIVE_CODE)
        fsm.registerLastState(self.GoneBehaviour(),     self.STATE_SIX_CODE)

        fsm.registerTransition(self.STATE_ZERO_CODE,  self.STATE_ZERO_CODE,  self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_ZERO_CODE,  self.STATE_ONE_CODE,   self.TRANSITION_TO_ONE)

        fsm.registerTransition(self.STATE_ONE_CODE,   self.STATE_ONE_CODE,   self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_ONE_CODE,   self.STATE_TWO_CODE,   self.TRANSITION_TO_TWO)

        fsm.registerTransition(self.STATE_TWO_CODE,   self.STATE_TWO_CODE,   self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_TWO_CODE,   self.STATE_THREE_CODE, self.TRANSITION_TO_THREE)

        fsm.registerTransition(self.STATE_THREE_CODE, self.STATE_THREE_CODE, self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_THREE_CODE, self.STATE_FOUR_CODE,  self.TRANSITION_TO_FOUR)
        fsm.registerTransition(self.STATE_THREE_CODE, self.STATE_FIVE_CODE,  self.TRANSITION_TO_FIVE)

        fsm.registerTransition(self.STATE_FOUR_CODE,  self.STATE_FOUR_CODE,  self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_FOUR_CODE,  self.STATE_ONE_CODE,   self.TRANSITION_TO_ONE)
        fsm.registerTransition(self.STATE_FOUR_CODE,  self.STATE_FIVE_CODE,  self.TRANSITION_TO_FIVE)

        fsm.registerTransition(self.STATE_FIVE_CODE,  self.STATE_FIVE_CODE,  self.TRANSITION_DEFAULT)
        fsm.registerTransition(self.STATE_FIVE_CODE,  self.STATE_SIX_CODE,   self.TRANSITION_TO_SIX)

        self.addBehaviour(fsm, None)

        template = spade.Behaviour.ACLTemplate()
        # template.setSender(spade.AID.aid("car1@" + host, ["xmpp://car1@" + host]))
        template.setOntology("Car2X")
        template.setProtocol("WAVE")
        t = spade.Behaviour.MessageTemplate(template)
        self.addBehaviour(self.RecvMsgBehaviour(), t)

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
        # self.neighbours.pop(neighbour)
        self.nb_pref.pop(nb_pref)
        print("Dict removal: " + str(self.nb_pref))

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

                elif self.status == "WAITING":

                    # Verifica se o vizinho está à direita
                    self.right_position   = self.myAgent.checkRightSide(self.origin)

                    self.change_direction = self.origin != self.dest

                    # Trata vizinhos que estiverem à direita
                    if not self.right_position:
                        self.myAgent.nb_pref[msg.getSender().getName()] = True
                    else:
                        self.myAgent.nb_pref[msg.getSender().getName()] = True if self.change_direction else False
                    #     self.right_position and !self.change_direction:
                    #     self.myAgent.nb_pref[msg.getSender().getName()] = False
                    # elif !self.right_position and self.change_direction:
                    #     self.myAgent.nb_pref[msg.getSender().getName()] = True
                    # else: #  !self.right and !self.change_direction:
                    #     self.myAgent.nb_pref[msg.getSender().getName()] = False



                    # self.myAgent.nb_pref[msg.getSender().getName()] = self.right
                    # self.myAgent.rightOfWay = False if self.right else True
                    # for nb in self.myAgent.nb_pref:
                        # if self.myAgent.nb_pref[nb] == False:
                            # self.myAgent.rightOfWay = True

                else: # self.status == "GONE"
                    # self.myAgent.removeNeighbour(msg.getSender())
                    # del self.myAgent.nb_pref[msg.getSender().getName()]
                    self.myAgent.nb_pref.pop(msg.getSender().getName())

                # Preferência dos vizinhos em relação a mim

                if bool(self.myAgent.nb_pref):
                    if self.myAgent.change_direction:
                        self.myAgent.rightOfWay = False
                    else:
                        self.myAgent.rightOfWay = False if False in self.myAgent.nb_pref.values() else True
                else:
                    self.myAgent.rightOfWay = True

                # if True in self.myAgent.nb_pref.values():
                #     self.myAgent.rightOfWay = False
                # else:
                    # if self.myAgent.change_direction:
                    #
                    #     if bool(self.myAgent.nb_pref):
                    #         self.myAgent.rightOfWay = False
                    #     else:
                    #         self.myAgent.rightOfWay = True

                # if self.myAgent.debug:
                    # print str(self.myAgent.getName()) + "| Messagem from " + str(msg.getSender().getName()) + ". Status " + self.status + " Origin " + self.origin + ". Right of way is " + str(self.right) + ". General right of way is " + str(self.myAgent.rightOfWay) + "."
                    # print self.myAgent.nb_pref
    """
    Comportamento de chegada de veículos ao cruzamento.
    """
    class ArriveBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            if self.myAgent.debug:
                print str(self.myAgent.getName()) + "| Arriving at crossing."
            time.sleep(1)
            self._exitcode = self.myAgent.TRANSITION_TO_ONE

    """
    Comportamento que envia mensagem de interesse em atravessar o cruzamento.
    """
    class HelloBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            # print str(self.myAgent.getName()) + "| Sending message."

            ######## send Message "Waiting" ########
            self.msg = self.myAgent.prepareMessage("WAITING")
            for receiver in self.myAgent.neighbours:
                self.msg.addReceiver(receiver)
            self.myAgent.send(self.msg)
            #######################################

            self._exitcode = self.myAgent.TRANSITION_TO_TWO

    """
    Comportamento que aguarda mensagens de outros agentes carros.
    """
    class WaitBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            # print str(self.myAgent.getName()) + "| Waiting."

            time.sleep(3)
            # print str(self.myAgent.getName()) + "| Waiting time is over."
            self._exitcode = self.myAgent.TRANSITION_TO_THREE

    """
    Comportamento decide o que fazer (aguardar ou atravessar) baseando-se nas
    normas.
    """
    class DecideBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            if self.myAgent.debug:
                print str(self.myAgent.getName()) + "| Deciding."
            time.sleep(3)

            # if permission_to_go && norms_checked

            if self.myAgent.rightOfWay :
                self._exitcode = self.myAgent.TRANSITION_TO_FIVE
            else:
                self._exitcode = self.myAgent.TRANSITION_TO_FOUR

    """
    Comportamento que dispara mensagem e espera para atravessar.
    """
    class DecideToStayBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            if self.myAgent.debug:
                print str(self.myAgent.getName()) + "| Staying."
            time.sleep(1)
            # if self.myAgent.getName() == "car1@127.0.0.1":
            self.myAgent.permission_to_go = True
            self._exitcode = self.myAgent.TRANSITION_TO_ONE

    """
    Comportamento que dispara mensagem e atravessa o cruzamento.
    """
    class DecideToGoBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            if self.myAgent.debug:
                print str(self.myAgent.getName()) + "| Coming."

            ######## send Message "Coming" ########
            self.msg = self.myAgent.prepareMessage("COMING")
            for receiver in self.myAgent.neighbours:
                self.msg.addReceiver(receiver)
            self.myAgent.send(self.msg)
            #######################################

            time.sleep(2)
            self._exitcode = self.myAgent.TRANSITION_TO_SIX

    """
    Comportamento que dispara mensagem e conclui a travessia do cruzamento.
    """
    class GoneBehaviour(spade.Behaviour.OneShotBehaviour):

        def _process(self):
            if self.myAgent.debug:
                print str(self.myAgent.getName()) + "| Crossing complete."

            ######## send Message "Gone" ##########
            self.msg = self.myAgent.prepareMessage("GONE")
            for receiver in self.myAgent.neighbours:
                self.msg.addReceiver(receiver)
            self.myAgent.send(self.msg)
            #######################################

            time.sleep(3)
            self._exitcode = self.myAgent.TRANSITION_TO_DEFAULT
            self.myAgent._kill()


# if __name__== "__main__":

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
#    red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
#    pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
#    yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)

    # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    # yellow = VehicleAgent("yellow@" + host, "secret", "NORTH", "NORTH", True)

    # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    # yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)
    #
    # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    # yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)

#    red.addNeighbour(pink.getAID())
#    red.addNeighbour(yellow.getAID())

#    pink.addNeighbour(red.getAID())
#    pink.addNeighbour(yellow.getAID())

#    yellow.addNeighbour(red.getAID())
#    yellow.addNeighbour(pink.getAID())

#    red.start()
#    pink.start()
#    yellow.start()

    # red.wui.start()
    # pink.wui.start()
    # yellow.wui.start()

    # red.setDebugToScreen()
    # pink.setDebugToScreen()
    # yellow.setDebugToScreen()
