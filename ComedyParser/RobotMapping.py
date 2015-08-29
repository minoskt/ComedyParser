import sys
import json
from math import hypot
from random import choice

from Robot import Robot


class RobotMapping:

    def __init__(self, calibration_file):

        # init Robot object
        self.robot = Robot()

        # open the file
        source = open(calibration_file, 'r')

        # print loading message
        print "Loading Calibration File..."

        # parse the json file
        self.calibration = json.load(source)

        # close the file
        source.close()

    def look(self, x, y):

        # get the head & torso
        head = self.robot.head
        torso = self.robot.torso

        # find the closest point
        values = self.closestpoint((x, y))

        # get the values
        nod = values["head_nod"]
        turn = values["head_turn"]
        roll = values["head_roll"]

        return {head.nod: nod,
                head.turn: turn,
                head.roll: roll,

                torso.bend: 1795,
                torso.sideways: 1799,
                torso.turn: 1815}

    def point(self, x, y):

        # find the closest point
        values = self.closestpoint((x, y))

        # get the two arms and torso
        arm_left = self.robot.arm_left
        arm_right = self.robot.arm_right
        torso = self.robot.torso

        # if on the left side, point with left hand
        if values["arm"] == 'left':

            # get the values
            up = values["arm_up"]
            out = values["arm_out"]
            elbow = values["arm_elbow"]

            dictionary = {arm_right.arm_up: 950,
                          arm_right.arm_out: 920,
                          arm_right.arm_twist: 1700,
                          arm_right.arm_elbow: 1350,

                          arm_right.hand.finger_index: 0,
                          arm_right.hand.finger_middle: 0,
                          arm_right.hand.finger_ring: 0,
                          arm_right.hand.finger_baby: 0,

                          arm_left.arm_up: up,
                          arm_left.arm_out: out,
                          arm_left.arm_twist: 1700,
                          arm_left.arm_elbow: elbow,

                          arm_left.hand.finger_index: 0,
                          arm_left.hand.finger_middle: 1,
                          arm_left.hand.finger_ring: 1,
                          arm_left.hand.finger_baby: 1,

                          torso.bend: 1795,
                          torso.sideways: 1799,
                          torso.turn: 1815}

        # else with the right
        elif values["arm"] == 'right':

            # get the values
            up = values["arm_up"]
            out = values["arm_out"]
            elbow = values["arm_elbow"]

            dictionary = {arm_right.arm_up: up,
                          arm_right.arm_out: out,
                          arm_right.arm_twist: 1700,
                          arm_right.arm_elbow: elbow,

                          arm_right.hand.finger_index: 0,
                          arm_right.hand.finger_middle: 1,
                          arm_right.hand.finger_ring: 1,
                          arm_right.hand.finger_baby: 1,

                          arm_left.arm_up: 950,
                          arm_left.arm_out: 920,
                          arm_left.arm_twist: 1700,
                          arm_left.arm_elbow: 1350,

                          arm_left.hand.finger_index: 0,
                          arm_left.hand.finger_middle: 0,
                          arm_left.hand.finger_ring: 0,
                          arm_left.hand.finger_baby: 0,

                          torso.bend: 1795,
                          torso.sideways: 1799,
                          torso.turn: 1815}

        else:
            print ("ERROR: Unknown arm type '%s'" % (values["arm"]))
            dictionary = None

        return dictionary

    def pointreset(self):

        # get the two arms and torso
        arm_left = self.robot.arm_left
        arm_right = self.robot.arm_right
        torso = self.robot.torso

        dictionary = {arm_right.arm_up: 950,
                      arm_right.arm_out: 920,
                      arm_right.arm_twist: 1700,
                      arm_right.arm_elbow: 1350,

                      arm_right.hand.finger_index: 0,
                      arm_right.hand.finger_middle: 0,
                      arm_right.hand.finger_ring: 0,
                      arm_right.hand.finger_baby: 0,

                      arm_left.arm_up: 950,
                      arm_left.arm_out: 920,
                      arm_left.arm_twist: 1700,
                      arm_left.arm_elbow: 1350,

                      arm_left.hand.finger_index: 0,
                      arm_left.hand.finger_middle: 0,
                      arm_left.hand.finger_ring: 0,
                      arm_left.hand.finger_baby: 0,

                      torso.bend: 1795,
                      torso.sideways: 1799,
                      torso.turn: 1815}

        return dictionary

    def pointBackLeft(self):

        # get the two arms, head and torso
        arm_right = self.robot.arm_right
        head = self.robot.head
        torso = self.robot.torso

        dictionary = {arm_right.arm_up: 1445,
                      arm_right.arm_out: 1480,
                      arm_right.arm_twist: 1989,
                      arm_right.arm_elbow: 1326,
                      arm_right.forearm: 1837,

                      arm_right.hand.wrist: 1848,

                      arm_right.hand.finger_index: 0,
                      arm_right.hand.finger_middle: 1,
                      arm_right.hand.finger_ring: 1,
                      arm_right.hand.finger_baby: 1,

                      torso.bend: 1881,
                      torso.sideways: 1786,
                      torso.turn: 1659,

                      head.nod: 1766,
                      head.turn: 1400,
                      head.roll: 1879}

        return dictionary

    def distance(self, point1, point2):
        return hypot(point2[0] - point1[0], point2[1] - point1[1])

    def closestpoint(self, point):

        # get all points from the list
        pointsList = [(element["shore_x"], element["shore_y"])
                      for element in self.calibration]

        # get the distance of all these posints ((x,y), distance)
        distanceList = [(element, self.distance(point, element))
                        for element in pointsList]

        # find the min distance
        minDistance = min(distance[1] for distance in distanceList)

        # find the point with that distance
        closestPoints = filter(lambda x: x[1] == minDistance, distanceList)

        # choose the first from the list (in case it is more than one)
        closestPoint = closestPoints[0][0]

        print closestPoint

        # find that element and return it
        return choice(filter(lambda x: (x["shore_x"] == closestPoint[0] and
                                        x["shore_y"] == closestPoint[1]),
                             self.calibration))


''' main '''
if __name__ == '__main__':

    # check if the the filename exists as a parameter
    if (len(sys.argv) < 1):
        sys.exit('Missing input file')

    # read the filename from the 1st argument
    filename = sys.argv[1]

    # init the RobotMapping
    mapping = RobotMapping(filename)

    print mapping.look(1, 3)
