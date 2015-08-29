class Robot:
    '''Outputs of the Robot'''

    def __init__(self):

        self.head = Head()
        self.torso = Torso()
        self.arm_left = Arm("left")
        self.arm_right = Arm("right")


class Head:

    def __init__(self):

        # ids
        self.nod = "87"
        self.turn = "116"
        self.roll = "88"


class Arm:

    def __init__(self, type):

        # add the hand
        self.hand = Hand(type)

        if type == "left":

            self.arm_up = "70"
            self.arm_out = "80"
            self.arm_twist = "68"
            self.arm_elbow = "67"
            self.forearm = "113"

        elif type == "right":

            self.arm_up = "64"
            self.arm_out = "66"
            self.arm_twist = "65"
            self.arm_elbow = "71"
            self.forearm = "114"

        else:
            print "WARNING: Unknown Arm type: " + type


class Hand:

    def __init__(self, type):

        if type == "left":

            # left fingers
            self.finger_index = "106"
            self.finger_middle = "107"
            self.finger_ring = "108"
            self.finger_baby = "109"

            self.wrist = "72"

        elif type == "right":

            # right fingers
            self.finger_index = "110"
            self.finger_middle = "93"
            self.finger_ring = "125"
            self.finger_baby = "126"

            self.wrist = "73"

        else:
            print "WARNING: Unknown Hand type: " + type


class Torso:

    def __init__(self):

        self.bend = "173"
        self.sideways = "175"
        self.turn = "174"
