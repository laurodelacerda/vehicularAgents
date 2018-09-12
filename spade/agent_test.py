# -*- coding: utf-8 -*-

from vehicleAgent import VehicleAgent

host = "127.0.0.1"

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
    #red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    #pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    #yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)

    red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    yellow = VehicleAgent("yellow@" + host, "secret", "NORTH", "NORTH", True)

    # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    # yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)
    #
    # red    = VehicleAgent("red@" + host, "secret", "EAST",  "NORTH", True)
    # pink   = VehicleAgent("pink@" + host, "secret", "WEST",  "WEST", True)
    # yellow = VehicleAgent("yellow@" + host, "secret", "SOUTH", "SOUTH", True)

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
