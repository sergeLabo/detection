# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.


from twisted.internet import reactor, protocol


class MyTCPServer(protocol.Protocol):
    """This is just about the simplest possible protocol"""

    def dataReceived(self, data):
        # # self.transport.write(data)
        print("data reçues dans le serveur:", data)


def main():
    """This runs the protocol on port 8000"""
    factory = protocol.ServerFactory()
    factory.protocol = MyTCPServer
    reactor.listenTCP(8000, factory)
    reactor.run()


if __name__ == "__main__":
    main()
