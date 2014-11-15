#!/usr/bin/env python

# A filename is expected as the first command-line argument.

import sys
import json
import os

from ComedyParser import ComedyParser


def askInput(parser):

    # ask for the user input
    userinput = raw_input('Command: ')

    # Quit command
    if userinput == "quit":

        # stop the parser
        parser.stop()

        print "Quitting..."

        # return, so quit
        return

    # Help command
    elif userinput == "help":
        print "quit: Quit"
        print "play: Play"

    # Play command
    elif userinput == "play":

        # Robot, play the comedy please!
        parser.play()

    # Continue, in case something goes wrong
    elif userinput == 'c':

        parser.resume()

    # Laughter Started, in case something goes wrong
    elif userinput == 'l':

        parser.laughing_on()

    # Applauding Started, in case something goes wrong
    elif userinput == 'a':

        parser.applauding_on()

    elif userinput.startswith('look'):

        # get the x and y
        x = int(userinput.split(' ')[1])
        y = int(userinput.split(' ')[2])

        parser.lookAt(x, y)

    elif userinput == '':

        parser.manual_tts_stop()

    # Unknown command
    else:
        print "Unknown command: " + userinput

    # ask for input again
    askInput(parser)


''' main '''
if __name__ == '__main__':

    # check if the the filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing input file')

    # read the filename from the 1st argument
    filename = sys.argv[1]

    # read the IP address
    # port is always 7766 (but can give an alternative if needed)
    if len(sys.argv) < 3:
        ip = "192.168.32.2"
        print "Choosing default IP address: %s" % (ip)
    else:
        ip = sys.argv[2]

    # open the file
    source = open(filename, 'r')

    # print loading message
    print "Loading Comedy Parser..."

    # parse the json file
    comedy = json.load(source)

    # close the file
    source.close()

    # parse the comedy with the robot on given IP address
    parser = ComedyParser(comedy, ip)

    # print some empty lines (separate from previous commands)
    for i in range(0, 50):
        print " "

    # clear screen
    os.system('clear')

    # print welcome message
    print "Welcome to Comedy Parser"
    print "------------------------"
    print

    # ask for user input
    askInput(parser)
