
from time import sleep
from multiprocessing import Process, Pipe
import json
import threading

from detection import main_in_process as my_detection

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ReconnectingClientFactory



class MyTCP(Protocol):

    def __init__(self, conn):

        self.conn = conn
        self.loop = 1
        self.relay_thread()
        print("Création d'un client TCP")

    def connectionLost(self, reason):
        print("Client TCP: deconnection:", reason)
        self.loop = 0

    def send(self, data):
        if self.transport:
            self.transport.write(data)

    def relay(self):
        while self.loop:
            try:
                data = self.conn.recv()
            except:
                data = None
            if data is not None:
                if data[0] == 'skelets':
                    self.send(data[1])
                elif data[0] == 'stop':
                    print("stop")
                    if reactor.running:
                        reactor.stop()

            sleep(0.02)

    def relay_thread(self):
        t = threading.Thread(target=self.relay)
        t.start()


class MyTCPClientFactory(ReconnectingClientFactory):

    def __init__(self, conn):
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



parent_conn, child_conn = Pipe()
p = Process(target=my_detection, args=(child_conn,))
p.start()

reactor.connectTCP('127.0.0.1', 8000, MyTCPClientFactory(parent_conn))
reactor.run()
