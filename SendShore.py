#!/usr/bin/env python

import sys
import socket
import time
import signal


def signal_handler(signal, frame):
        s.close()
        sys.exit(0)

''' main '''
if __name__ == '__main__':

    # register for catching Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)

    # check if the the input filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing shore input file')

    # check if the the input filename exists as a parameter
    if (len(sys.argv) < 3):
        sys.exit('Missing IP address')

    # read files from arguments
    inputFile = sys.argv[1]

    # read the ip address
    ip = ''  # sys.argv[2]
    port = 50007

    # open files
    source = open(inputFile, 'r')

    print "connecting..."

    # open the connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    print "connected!"

    # loop through file with .1sec sleep on every frame
    lastFrame = None

    for line in source:

        # get the frame number
        frame = line.split(' ')[0].split('=')[1]

        # sleep for every new frame
        if lastFrame != frame:
            lastFrame = frame
            time.sleep(0.1)  # simulate 10 frame / sec

        # parse the line
        s.send(line)
        s.recv(1024)
        print line

    # file is now finished
    # close the connection and exit
    s.close()
