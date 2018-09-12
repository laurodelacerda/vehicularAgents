import spade
import time

host = "127.0.0.1"

class Sender(spade.Agent.Agent):

    def __init__(self, _ip, _pass):
        myip   = _ip
        mypass = _pass
        spade.Agent.Agent.__init__(self, _ip, _pass)



    def _setup(self):
		self.addBehaviour(self.SendMsgBehav())
		print "Agent started!"

    class SendMsgBehav(spade.Behaviour.OneShotBehaviour):
        """
        This behaviour sends a message to this same agent to trigger an EventBehaviour
        """

        def _process(self):
            self.msg = spade.ACLMessage.ACLMessage()
            self.msg.setOntology("Car2X")
            self.msg.setProtocol("WAVE")
            self.myAgent.send(self.msg)

    class RecvMsgBehav(spade.Behaviour.EventBehaviour):
        """
        This EventBehaviour gets launched when a message that matches its template arrives at the agent
        """

        def _process(self):
            self.msg = self._receive(True, None)
            print str(myip) + " | " + "This behaviour has been triggered by a message!"


        def _setup(self):

            template = spade.Behaviour.ACLTemplate()
            # template.setSender(spade.AID.aid("car1@" + host, ["xmpp://car1@" + host]))
            template.setOntology("Car2X")
            template.setProtocol("WAVE")
            t = spade.Behaviour.MessageTemplate(template)
            self.addBehaviour(self.RecvMsgBehav(), t)

            # Add the sender behaviour
            self.addBehaviour(self.SendMsgBehav())

if __name__ == "__main__":
    a = Sender("a@" + host, "secret")
    a.start()

    b = Sender("b@" + host, "secret")
    b.start()
