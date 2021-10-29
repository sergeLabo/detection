class Skelet3DOSC:
    """OSC ne peut envoyer que des listes de int ou float, pas de liste de liste

    squelettes 3D = [[ 17 items, soit 3 coordonnées, soit None],
                        [ 17 items, soit 3 coordonnées, soit None],
                        ...]
    Concaténé en une liste:
        Pour 2 skelets
        liste de 2 x 17 x 3 = 102 items
    Les points None sont convertit en [100000, 100000, 100000]
    OSC ne connait pas None, ni null
    """

    def encode(self, skelet_3D):
        # Le message OSC qui sera envoyé obtenu dans encode
        self.message = []

    def decode(self):
        """Decode les squelettes reçus en
        liste de [ 17 items, soit 3 coordonnées, soit None]
        """

        return skelet_3D
