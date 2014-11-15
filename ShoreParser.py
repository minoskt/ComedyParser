#!/usr/bin/env python

import sys
import json
import re
from datetime import datetime


def parseLine(line):
    '''Parse the line and return in dictionary'''

    # use ', ' as a separator
    line = _transformLine(line)

    # empty dict
    dictionary = {}

    # iterate through items
    for item in line.split(', '):

        # get the key and value from the item
        key, value = _parseItem(item)

        # cast value based on the key
        if (key in ['Left', 'Top', 'Right', 'Bottom']):

            # float to int value
            if value:
                try:
                    value = int(float(value) * 1000)
                except:
                    value = 0

        elif (key in ['Uptime', 'Score', 'Surprised', 'Sad', 'Happy', 'Angry',
                      'Age', 'MouthOpen', 'LeftEyeClosed', 'RightEyeClosed']):

            # float value
            if value:
                try:
                    value = float(value)
                except:
                    value = 0

        elif (key in ['Id', 'Frame']):

            # int value
            if value:
                try:
                    value = int(value)
                except:
                    value = 0

        elif (key == 'TimeStamp'):

            try:
                # save it as a datetime object
                value = _parseDate(value)
            except:
                None

        # add to the dictionary
        dictionary[key] = value

    # return
    return dictionary


def _parseDate(date):
    '''Parse a date in string and return a datetime object'''

    if len(date) == 20:
        # Datetime format: '2013-Jul-02 16:32:46'
        value = datetime.strptime(date, '%Y-%b-%d %H:%M:%S')
    else:
        # Datetime format: '2013-Jul-02 16:32:46.396849'
        value = datetime.strptime(date, '%Y-%b-%d %H:%M:%S.%f')

    return value


def _parseItem(item):
    '''Parse the item and return key, value (in string)'''

    # format should be key=value
    itemList = item.split('=')

    # normal case (key=value)
    if len(itemList) == 2:

        # set the key
        key = itemList[0]

        # set the value
        if itemList[1] == 'nil':
            value = None
        else:
            value = itemList[1]

    # handle the case where value is missing (e.g. 'Gender=')
    elif len(itemList) == 1:

        # set the key
        key = itemList[0]

        # set the value to None
        value = None

    else:
        sys.exit('Error: structure of input file is invalid. Item: ' + item)

    # return
    return key, value


def _transformLine(line):
    '''Replace space separators with ", "
       and only use space in the TimeStamp'''

    return re.sub(r'[ ]([a-zA-Z])', r', \1', line)


''' main '''
if __name__ == '__main__':

    # check if the the input filename exists as a parameter
    if (len(sys.argv) < 2):
        sys.exit('Missing input file')

    # read files from arguments
    inputFile = sys.argv[1]

    # open files
    source = open(inputFile, 'r')

    # parse each line
    for line in source:

        # don't return anything, it is just for testing
        parseLine(line)

    # close files
    source.close()
