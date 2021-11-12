

"""
Script principal pour la détection.

Les autres scripts sont les lib pour la caméra, la détection des squelettes,
les outils.

Capture de 1 à 4 squelettes
avec
camera Intel RealSense D455, Google posenet et Google Coral.

Définition des variables:

Articulations:
    - keypoints: définis dans la class KeypointType de my_posenet_conversion.py

Un squelette 2D = xys:
    - liste de 17 items avec les coordonnées de chaque keypoints
    - xys_list = [(698, 320), (698, 297), None, ... ]
    - il y a toujours 17 items, si le point n'est pas détecté, la value est None
    - Un squelette contient toujours au moins un keypoint.
Tous les squelettes sont dans une liste = skelets_2D

Un squelette 3D:
    - liste de 17 items, soit 3 coordonnées, soit None
Tous les squelettes 3D sont dans une liste = skelets_3D

Nommage des axes:
    - x et y viennent de l'image 2D
    - x est horizontal latéral
    - y est la verticale
    - z est la profondeur: projection sur l'axe de vision de la caméra
    de la distance du pixel au centre de la caméra

Origine, sens des axes:
    - Dans une image 2D, origine = en haut à gauche,
    sens x positif vers la droite, sens des y positif vers le bas
    - Dans l'espace, vue depuis la caméra:
        - x positif vers la droite
        - y positif vers le haut
        - z positif en s'éloignant de la camera
"""


from time import time, sleep
import json

import numpy as np
import cv2

from my_posenet_conversion import MyPoseNetConversion
from posenet.my_posenet import MyPosenet
from posenet.pose_engine import EDGES

from my_realsense import MyRealSense
import pyrealsense2 as rs

from my_config import MyConfig



class Viewer:

    def __init__(self, **kwargs):
        # Fenêtres OpenCV
        cv2.namedWindow('color', cv2.WND_PROP_FULLSCREEN)

        # Loop OpenCV
        self.loop = 1

        # Clacul du FPS
        self.t0 = time()
        self.nbr = 0

        # Suivi
        self.frame = 0

    def viewer(self):
        # ############### Affichage de l'image
        cv2.imshow('color', self.color_arr)

        # Calcul du FPS, affichage toutes les 10 s
        if time() - self.t0 > 10:
            print("FPS =", int(self.nbr/10))
            self.t0, self.nbr = time(), 0

        k = cv2.waitKey(1)
        # Pour quitter
        if k == 27:  # Esc
            self.loop = 0
            self.conn.send(["stop", 0])
            self.close()

    def close(self):
        cv2.destroyAllWindows()



class Detection(Viewer):
    """Capture, détection des squelettes."""

    def __init__(self, **kwargs):
        """La config est dans detection.ini"""

        super().__init__(**kwargs)

        self.config = kwargs
        print(f"Configuration de Detection:\n{self.config}\n\n")

        # Le Pipe du multiprocess
        if 'conn' in self.config:
            self.conn = self.config['conn']
        else:
            self.conn = None

        # Seuil de confiance de reconnaissance du squelette
        self.threshold = float(self.config['pose']['threshold'])

        # Nombre de pixels autour du point pour moyenne du calcul de profondeur
        self.around_d = int(self.config['pose']['around_distance'])

        # Taille d'image possible: 1280x720, 640x480 seulement
        # 640x480 est utile pour fps > 30
        # Les modèles posenet imposent une taille d'image
        self.width = int(self.config['camera']['width_input'])
        self.height = int(self.config['camera']['height_input'])

        # Appel de la class de gestion de la caméra
        self.my_rs = MyRealSense(**self.config)
        self.my_rs.set_pipeline()

        # Appel de la reconnaissance de squelette
        self.my_posenet = MyPosenet(self.width, self.height)

        self.skelets_2D, self.skelets_3D = None, None

    def run(self):
        """Boucle infinie, quitter avec Echap dans la fenêtre OpenCV"""

        while self.loop:
            self.nbr += 1
            self.frame += 1

            # ############### RealSense
            frames = self.my_rs.pipeline.wait_for_frames(timeout_ms=80)

            # Align the depth frame to color frame
            aligned_frames = self.my_rs.align.process(frames)

            color = aligned_frames.get_color_frame()
            self.depth_frame = aligned_frames.get_depth_frame()

            if not self.depth_frame and not color:
                continue

            color_data = color.as_frame().get_data()
            self.color_arr = np.asanyarray(color_data)

            # ############### Posenet
            outputs = self.my_posenet.get_outputs(self.color_arr)

            # Recherche des squelettes
            self.main_frame(outputs)

            # Envoi sur Pipe
            if self.conn:
                data = json.dumps(self.skelets_3D) + '\n'
                self.conn.send(["skelets", data.encode('ascii')])

            self.viewer()

    def main_frame(self, outputs):
        """ Appelé depuis la boucle infinie, c'est le main d'une frame.
                Récupération de tous les squelettes
        """

        self.skelets_2D, self.skelets_3D = None, None

        # Récupération de tous les squelettes
        if outputs:
            # liste des squelettes 2D, un squelette = dict de 17 keypoints
            self.skelets_2D = MyPoseNetConversion(outputs, self.threshold).skeletons

            if self.skelets_2D:
                # Ajout de la profondeur pour 3D, et capture des couleurs
                # Liste des squelettes 3D, un squelette = list de 17 keypoints
                # un keypoint = liste de 3 coordonnées
                self.skelets_3D = self.get_skelets_3D()

        self.draw_all_poses()

    def get_skelets_3D(self):
        """A partir des squelettes 2D détectés dans l'image,
        retourne les squelettes 3D
        """
        skelets_3D = []
        for xys in self.skelets_2D:
            pts = self.get_points_3D(xys)
            if pts:
                skelets_3D.append(pts)
        return skelets_3D

    def get_points_3D(self, xys):
        """Trouve les points 3D pour un squelette"""

        # Les coordonnées des 17 points 3D avec qq None
        points_3D = [None]*17

        # Parcours des squelettes
        for i, xy in enumerate(xys):
            if xy:
                x = xy[0]
                y = xy[1]
                # Calcul de la profondeur du point
                profondeur = self.get_profondeur(x, y)
                if profondeur:
                    # Calcul les coordonnées 3D avec x et y coordonnées dans
                    # l'image et la profondeur du point
                    # Changement du nom de la fonction trop long
                    point_2D_to_3D = rs.rs2_deproject_pixel_to_point
                    point_with_deph = point_2D_to_3D(self.my_rs.depth_intrinsic,
                                                     [x, y],
                                                     profondeur)
                    # Conversion des m en mm
                    points_3D[i] = [int(1000*x) for x in point_with_deph]

        if points_3D == [None]*17:
            # Tous les points sont inférieur à la valeur du threshold
            return None

        return points_3D

    def get_profondeur(self, x, y):
        """Calcul la moyenne des profondeurs des pixels autour du point considéré
        Filtre les absurdes et les trop loins
        """
        profondeur = None
        distances = []
        # around = nombre de pixel autour du points
        x_min = max(x - self.around_d, 0)
        x_max = min(x + self.around_d, self.depth_frame.width)
        y_min = max(y - self.around_d, 0)
        y_max = min(y + self.around_d, self.depth_frame.height)

        for u in range(x_min, x_max):
            for v in range(y_min, y_max):
                # Profondeur du point de coordonnée (u, v) dans l'image
                distances.append(self.depth_frame.get_distance(u, v))

        # Si valeurs non trouvées, retourne [0.0, 0.0, 0.0, 0.0]
        # Remove the item 0.0 for all its occurrences
        dists = [i for i in distances if i != 0.0]
        dists_sort = sorted(dists)
        if len(dists_sort) > 2:
            # Suppression du plus petit et du plus grand
            goods = dists_sort[1:-1]
            # TODO: rajouter un filtre sur les absurdes ?

            # Calcul de la moyenne des profondeur
            profondeur = get_average_list_with_None(goods)

        return profondeur

    def draw_all_poses(self):
        if self.skelets_2D:
            for skelet in self.skelets_2D:
                if skelet:
                    self.draw_pose(skelet, [0, 255, 255])

    def draw_pose(self, xys, color):
        """Affiche les points 2D, et les 'os' dans l'image pour un acteur
        xys = [[790, 331], [780, 313], None,  ... ]
        """

        # Dessin des points
        for point in xys:
            if point:
                x = point[0]
                y = point[1]
                cv2.circle(self.color_arr, (x, y), 5, color=(100, 100, 100),
                                                                  thickness=-1)
                cv2.circle(self.color_arr, (x, y), 6, color=color, thickness=1)

        # Dessin des os
        for a, b in EDGES:
            a = a.value  # 0 à 16
            b = b.value  # 0 à 16

            # Os seulement entre keypoints esxistants
            if not xys[a] or not xys[b] :
                continue

            # Les 2 keypoints esxistent
            ax, ay = xys[a]
            bx, by = xys[b]
            cv2.line(self.color_arr, (ax, ay), (bx, by), color, 2)




def get_average_list_with_None(liste):
    """Calcul de la moyenne des valeurs de la liste, sans tenir compte des None.
    liste = list de int ou float
    liste = [1, 2, None, ..., 10.0, None]

    Retourne un float
    Si la liste ne contient que des None, retourne None
    """
    # dtype permet d'accepter les None
    liste_array = np.array(liste, dtype=np.float64)

    return np.nanmean(liste_array)


def main():

    ini_file = './detection.ini'
    config_obj = MyConfig(ini_file)
    config = config_obj.conf

    detect = Detection(**config)
    detect.run()


def main_in_process(conn):

    ini_file = './detection.ini'
    config_obj = MyConfig(ini_file)
    config = config_obj.conf

    config['conn'] = conn
    detect = Detection(**config)
    detect.run()


if __name__ == '__main__':

    main()
