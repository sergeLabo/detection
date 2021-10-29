

import enum


class KeypointType(enum.IntEnum):
    """Pose kepoints."""
    NOSE = 0
    LEFT_EYE = 1
    RIGHT_EYE = 2
    LEFT_EAR = 3
    RIGHT_EAR = 4
    LEFT_SHOULDER = 5
    RIGHT_SHOULDER = 6
    LEFT_ELBOW = 7
    RIGHT_ELBOW = 8
    LEFT_WRIST = 9
    RIGHT_WRIST = 10
    LEFT_HIP = 11
    RIGHT_HIP = 12
    LEFT_KNEE = 13
    RIGHT_KNEE = 14
    LEFT_ANKLE = 15
    RIGHT_ANKLE = 16



class PoseNetConversion:
    def __init__(self, outputs, threshold):

        self.outputs = outputs
        self.threshold = threshold
        self.skeletons = []
        self.conversion()

    def conversion(self):
        """Convertit les keypoints posenet dans ma norme"""
        self.skeletons = []
        for pose in self.outputs:
            xys = self.get_points_2D(pose)
            self.skeletons.append(xys)

    def get_points_2D(self, pose):
        """ ma norme = dict{index du keypoint: (x, y), }
        xys = {0: (698, 320), 1: (698, 297), 2: (675, 295), .... }
        """
        xys = {}
        for label, keypoint in pose.keypoints.items():
            if keypoint.score > self.threshold:
                xys[label.value] = [int(keypoint.point[0]),
                                    int(keypoint.point[1])]
        return xys
