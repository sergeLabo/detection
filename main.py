
from time import sleep
from multiprocessing import Process, Pipe
import json
import threading

from detection import main_in_process as my_detection

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory



class MyTCP(Protocol):
    """Un client TCP seul et simple"""

    def __init__(self, conn):
        """conn est le connecteur Pipe du Process"""
        self.conn = conn
        self.loop = 1
        self.relay_thread()
        print("Création d'un client TCP")

    def connectionLost(self, reason):
        print("Client TCP: deconnection:", reason)
        # Fin de la boucle infinie pour terminer le thread
        self.loop = 0

    def send(self, data):
        if self.transport:
            self.transport.write(data)

    def relay(self):
        """Boucle infinie qui envoie en TCP ce qui est reçu par le Pipe"""
        while self.loop:
            try:
                data = self.conn.recv()
            except:
                data = None
            if data is not None:
                # Réenvoi en TCP des skelets
                if data[0] == 'skelets':
                    self.send(data[1])
                    print(data[1])
                # Fin du client si echap dans la fenêtre OpenCV
                elif data[0] == 'stop':
                    print("stop")
                    if reactor.running:
                        reactor.stop()
            sleep(0.02)

    def relay_thread(self):
        t = threading.Thread(target=self.relay)
        t.start()



class MyTCPClientFactory(ReconnectingClientFactory):
    """L'usine qui fabrique les clients et permet une reconnexion.
    Le  délai entre 2 tentatives augmente progressivement
    """
    def __init__(self, conn):
        """conn est le connecteur Pipe du Process"""
        self.conn = conn

    def startedConnecting(self, connector):
        print('Started to connect.')

    def buildProtocol(self, addr):
        print('Connected.')
        print('Resetting reconnection delay')
        self.resetDelay()
        return MyTCP(self.conn)

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.  Reason:', reason)
        ReconnectingClientFactory.clientConnectionLost(self, connector, reason)

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed. Reason:', reason)
        ReconnectingClientFactory.clientConnectionFailed(self, connector,
                                                         reason)



# La com entre les 2 processus
parent_conn, child_conn = Pipe()

# 2ème processus
p = Process(target=my_detection, args=(child_conn,))
p.start()

# 1er processus qui est le script ici
reactor.connectTCP('192.168.1.128', 55555, MyTCPClientFactory(parent_conn))
reactor.run()
