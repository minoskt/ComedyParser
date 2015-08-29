#!/usr/bin/env python

import sys
from UserString import MutableString


def parseEvent(event, destination):
    pass


def parsefile(source, destination):

    for line in source:

        if (
            line.find("Torso") == -1
            and line.find("Head") == -1
            and line.find("Eye") == -1
        ):

            # write it
            destination.write(line)

        # else skip it


''' main '''
if __name__ == '__main__':

    # check if the  input filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing input file')

    # check if the output filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing output file')

    # read the filename from the 1st argument
    inputfilename = sys.argv[1]
    outputfilename = sys.argv[2]

    # open the input file
    source = open(inputfilename, 'r')
    destination = open(outputfilename, 'w')

    # parse the file
    parsefile(source, destination)

    # close files
    source.close()
    destination.close()
