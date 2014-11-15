#!/usr/bin/env python

import sys
import json
import os
import time 

from Communication import CommunicationModule
from AudienceAnalyser import AudienceAnalyser

class Calibration:
    """CommunicationModule Class"""

    def __init__(self):

        # init the list
        self.data = []

        # init the tmp dict
        self.temp_dict = {}

        # init communication module
        self.comm = CommunicationModule('192.168.32.2', 7766)

        # init the AudienceAnalyser
        self.audienceAnalyser = AudienceAnalyser(1, self.callback, self.callback)

        # start the audience analyser
        self.audienceAnalyser.start()

        # connect, auth and start keep-alive thread
        self.comm.connect()

        # just wait one sec
        time.sleep(1)

    def callback(self):
        None

    def save(self, filename):

        jsonarray = json.dumps(self.data, indent=4)

        file = open(filename + ".json", "w")
        file.write(jsonarray)
        file.close()

        print "Saved!"

    def addPoint(self, parameter, value):

        if parameter == "arm":
            self.temp_dict[parameter] = value
        else:
            self.temp_dict[parameter] = int(value)

        # if size is full, add it and print message
        # if all valid
        if len(self.temp_dict) == 10:

            # add to data
            self.data.append(self.temp_dict)

            # empty it
            self.temp_dict = {}

            print "Added the point."

        
    def add(self, chair, hand, x, y):

        def callback(parameter, value):
            self.addPoint(parameter, value)

        # start with True
        valid = True

        # check hand
        if (hand not in ["l", "r"]):
            valid = False
            print "Hand can only be 'l' or 'r'"

        # check chair number
        try:
            chair = int(chair)
        except:
            valid = False
            print "Non valid chair number. Should be an Integer."

        person = self.audienceAnalyser.audience.getRandomPerson()


        if valid == True:
            
            # fix hand value
            if hand == "l":
                hand = "left"

                self.comm.command_output_read('arm_up', '70', callback)
                self.comm.command_output_read('arm_out', '80', callback)
                self.comm.command_output_read('arm_elbow', '67', callback)

            elif hand == "r":
                hand = "right"

                self.comm.command_output_read('arm_up', '64', callback)
                self.comm.command_output_read('arm_out', '66', callback)
                self.comm.command_output_read('arm_elbow', '71', callback)

            # do the calls
            self.addPoint('shore_x', x)
            self.addPoint('shore_y', y)
            self.addPoint('chair', chair)
            self.addPoint('arm', hand)
            self.comm.command_output_read('head_nod', '87', callback)
            self.comm.command_output_read('head_turn', '116', callback)
            self.comm.command_output_read('head_roll', '88', callback)

        else:
            print "Calibration point was not added"


    def askInput(self):

        # ask for the user input
        userinput = raw_input('Command: ')

        # Quit command
        if userinput == "quit":

            # disconnect
            self.comm.disconnect()

            print "Quitting..."

            # return, so quit
            return

        # add command
        elif userinput.startswith('add'):

            # chair no
            chair = userinput.split(' ')[1]

            # left/right
            hand = userinput.split(' ')[2]

            # x
            x = userinput.split(' ')[3]

            # y
            y = userinput.split(' ')[4]

            # add it
            self.add(chair, hand, x, y)
     
        elif userinput.startswith('save'):
            
            # filename
            filename = userinput.split(' ')[1]

            self.save(filename)

        # Unknown command
        else:
            print "Unknown command: " + userinput

        # ask for input again
        self.askInput()


''' main '''
if __name__ == '__main__':

    # init calibration
    calibration = Calibration()

    # print some empty lines (separate from previous commands)
    for i in range(0, 50):
        print " "

    # clear screen
    os.system('clear')

    # print welcome message
    print "Calibration"
    print "-------------"
    print

    # ask for user input
    calibration.askInput()