#!/usr/bin/env python

import sys
import time
import random
import threading
import re
import heapq
import socket
import numpy

from UserString import MutableString
from datetime import timedelta
from datetime import datetime
from ReadShore import ReadShore

import ShoreParser as sp
import LaughStateEstimator as lse

from FileLogger import FileLogger

# size of the buffered values for each person
buffer_time = 3  # secs


class AudienceAnalyser:
    ''' Audience class '''

    def __init__(self, expectedPeople, laughStartCallback, laughStopCallback):

        # init FileLoger
        self._logger = FileLogger('log_ShoreFrames')

        # save the callbacks
        self._laughStartCallback = laughStartCallback
        self._laughStopCallback = laughStopCallback

        # init the Audience
        self.audience = Audience(expectedPeople)

        # init ReadShore module
        self._readShore = ReadShore(self._shoreDataReceived)

        # initialise the basic random generator
        random.seed()
        
        # last known audience laugh state
        self.laughStateLast = 'Not Laughing'

    def _shoreDataReceived(self, data):

        # read the data
        self.read(data)
        #print data

    def start(self):

        # start the readShore thread
        self._readShore.start()

    def stop(self):
        pass

    def read(self, shoreLine):

        # convert shoreLine into dict
        line = sp.parseLine(shoreLine)

        if ('Frame' in line.keys() and
            'Left' in line.keys() and
            'Top' in line.keys() and
            'Right' in line.keys() and
            'Bottom' in line.keys()):

            # pass the dict to the Audience object
            self.audience.read(line)

            # log frame
            self._logger.log("Shore frame '%d'" % (line['Frame']))
        
            # determine audience laugh state
            
            if self.laughStateLast == 'Not Laughing':
                if self.audience.laughProportion() > 0.333:
                    self.laughStateLast = 'Laughing'
                    self._laughStartCallback()
            elif self.laughStateLast == 'Laughing':
                if self.audience.laughProportion() < 0.111:
                    self.laughStateLast = 'Not Laughing'
                    self._laughStopCallback()

class Audience:
    '''Audience class'''

    def __init__(self, expectedPeople):

        # init the list of Persons
        self._people = []

        # init the frames counter
        self._frames = 0
        self._lastFrame = None

        # save expected people
        self._expectedPeople = expectedPeople

        # init refered people dict
        self._refPeople = {}

    def read(self, shoreDict):

        if ('Frame' in shoreDict.keys() and
            'Left' in shoreDict.keys() and
            'Top' in shoreDict.keys() and
            'Right' in shoreDict.keys() and
            'Bottom' in shoreDict.keys()):

            # check if it is a new frame
            if shoreDict['Frame'] != self._lastFrame:

                # set new frame to all People
                self.newFrame(self._lastFrame)

                # increase it and save it
                self._frames += 1
                self._lastFrame = shoreDict['Frame']

            # add the person to the list
            self._addPerson(shoreDict)

    def newFrame(self, frame):

        # iterate through people list
        for person in self._people:
            
            # end frame
            person.newFrame(frame)

    def _addPerson(self, shoreDict):

        # get the frame
        frame = Frame(shoreDict['Left'], shoreDict['Top'],
                      shoreDict['Right'], shoreDict['Bottom'])


        # check if that person exists on the list
        person = self._personExists(frame)

        # if not
        if person is None:

            # create the object
            person = Person()

            # update it with current data
            person.update(frame, shoreDict)

            # add it to the list
            self._people.append(person)

        else:
            # just update it
            person.update(frame, shoreDict)
            x, y = frame.center()

            # Calibrate
            #print "x:" + str(x) + " y:" + str(y)
    
    def _personExists(self, frame):
        ''' check if that person exists in the list '''

        # iterate through people list
        for person in self._people:

            # if a person exists
            if (person.isCloseTo(frame)):
                return person

        return None

    def getValidPeople(self):
        ''' Check the people array and only return the valid ones '''

        # return the max N persons of the array
        # N = self._expectedPeople
        if self._people:
            return heapq.nlargest(self._expectedPeople,
                                  self._people, key=lambda x: x.identified)
        else:
            return None

    def laughProportion(self):
        laughStates = [x.laughState() for x in self._people]
        laughCount = laughStates.count('Laughing')
        totalCount = len(self.getValidPeople())
        
        laughProp = float(laughCount)/totalCount
        
        # print 'Laughing {}/{} {}'.format(laughCount, totalCount, laughProp)
        
        return laughProp

    def laughState(self):
        
        if self.laughProportion() > 0.3333333333:
            return 'Laughing'
        else:
            return 'Not Laughing'
        
        # # we could try a more sophisticated audience laugh state evaluation than just comparing indiviual states
        # audienceSmileValence = 0
        # audienceBobValence = 0
        # 
        # for person in self._people:
        #     plse = person.laughStateEstimator
        #     
        #     if None not in [plse.happinessCurrent, plse.happinessThreshold, plse.bobbingCurrent, plse.bobbingThreshold]:
        #         audienceSmileValence += plse.happinessCurrent - plse.happinessThreshold
        #         audienceBobValence += plse.bobbingCurrent - plse.bobbingThreshold
        # 
        # if audienceSmileValence > 0:
        #     
        #     if audienceBobValence > 0:
        #         return 'Laughing'
        #     else:
        #         return 'Smiling'
        # else:
        #     return 'Not Laughing'

    def statistics(self):

        # use MutableString for efficiency
        statistics = MutableString()

        # count of persons (all and valid)
        validPeople = len(self.getValidPeople())
        allPeople = len(self._people)

        statistics += ("Valid People: " + str(validPeople) +
                       " of " + str(allPeople) + "\n")

        # add statistics about each identified person
        for person in self.getValidPeople():

            # statistics
            statistics += "Person_" + str(person.id) + ": "
            statistics += str(person.identified) + "\n"

        return statistics

    def getRandomPerson(self):

        # get all valid people
        validPeople = self.getValidPeople()

        # random
        if validPeople:
            return random.choice(validPeople)
        else:
            return None

    def savePerson(self, person, reference_id):

        # save the person's id with the reference_id
        self._refPeople[reference_id] = person.id

    def getRefPerson(self, reference_id):

        # get the real id from the reference_id
        personId = self._refPeople[reference_id]

        # search for the previously saved person
        # should be in all peopla and not only valid ones
        return filter(lambda x: x.id == personId, self._people)[0]

    def getHappiestPerson(self):

        # get all valid people
        validPeople = self.getValidPeople()

        # get the person with the highest value in happiness
        if validPeople:

            # get the max happy value
            maxValue = max(person.happy() for person in validPeople)

            # get all people with that value
            maxPeople = filter(lambda x: x.happy() == maxValue, validPeople)

            # return a random one
            if maxPeople:
                return random.choice(maxPeople)
            else:
                return None

        else:
            return None

    def getUnhappiestPerson(self):

        # get all valid people
        validPeople = self.getValidPeople()

        # get the person with the lowest value in happiness
        if validPeople:

            # get the min happy value
            minValue = min(person.happy() for person in validPeople)

            # get all people with that value
            minPeople = filter(lambda x: x.happy() == minValue, validPeople)

            # return a random one
            if minPeople:
                return random.choice(minPeople)
            else:
                return None

        else:
            return None

    def getYoungestPerson(self):

        # get all valid people
        validPeople = self.getValidPeople()

        # get the person with the lowest value in happiness
        if validPeople:

            # get the min age value
            minValue = min(person.age() for person in validPeople)

            # get all people with that value
            minPeople = filter(lambda x: x.age() == minValue, validPeople)

            # return a random one
            if minPeople:
                return random.choice(minPeople)
            else:
                return None

        else:
            return None

    def getHappiestPersonWithGender(self, gender):

        # get all valid people
        validPeople = self.getValidPeople()

        # get the person with the highest value in happiness
        if validPeople:

            # get the max happy value
            maxValue = max(person.happy() for person in validPeople
                           if person.gender() == gender)

            # get all people with that value
            maxPeople = filter(lambda x: x.happy() == maxValue
                               and x.gender() == gender,
                               validPeople)

            # return a random one
            if maxPeople:
                return random.choice(maxPeople)
            else:
                return None

        else:
            return None


class Person:
    '''Person class'''
    _counter = 0

    def __init__(self):

        # set the id
        self.id = Person._counter
        Person._counter += 1

        # Debug
        #print "New Person: " + str(Person._counter)

        # init the identified
        self.identified = 0

        # init list structures
        self._systemtimestamp = []
        self._timestamp = []
        self._uptime = []
        self._score = []
        self._gender = []
        self._surprised = []
        self._sad = []
        self._happy = []
        self._angry = []
        self._age = []
        self._mouthOpen = []
        self._leftEyeClosed = []
        self._rightEyeClosed = []
        self._laughState = []

        # init response as None [None, 'Smiling', 'Laughing']
        self.response = None
        
        # init laughStateEstimator instance
        self.laughStateEstimator = lse.LaughStateEstimator()

    def update(self, frame, shoreDict):

        # increase the identified var
        self.identified += 1

        # update the frame
        self.frame = frame

        # add system datetime.now()
        self._systemtimestamp.append(datetime.now())

        # add values to buffer lists
        self._addToBuffer(shoreDict, 'TimeStamp', self._timestamp)
        self._addToBuffer(shoreDict, 'Uptime', self._uptime)
        self._addToBuffer(shoreDict, 'Score', self._score)
        self._addToBuffer(shoreDict, 'Gender', self._gender)
        self._addToBuffer(shoreDict, 'Surprised', self._surprised)
        self._addToBuffer(shoreDict, 'Sad', self._sad)
        self._addToBuffer(shoreDict, 'Happy', self._happy)
        self._addToBuffer(shoreDict, 'Angry', self._angry)
        self._addToBuffer(shoreDict, 'Age', self._age)
        self._addToBuffer(shoreDict, 'MouthOpen', self._mouthOpen)
        self._addToBuffer(shoreDict, 'LeftEyeClosed', self._leftEyeClosed)
        self._addToBuffer(shoreDict, 'RightEyeClosed', self._rightEyeClosed)
        
        self.laughStateEstimator.analyseWithShoreDict(shoreDict)
        self._addToBuffer(shoreDict, 'LaughState', self._laughState)

    def _addToBuffer(self, shoreDict, dictkey, bufferlist):

        # check if the key exists
        if dictkey in shoreDict.keys():

            # add it the the appropriate  list
            bufferlist.append(shoreDict[dictkey])
        else:

            # add None
            bufferlist.append(None)

    def newFrame(self, frame):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

    def _checkTimeStamp(self):

        # find the timestamp - buffer_time
        comparetimestamp = datetime.now() - timedelta(seconds=buffer_time)

        # find the indexes
        indexes = [index for index, _timestamp in enumerate(self._timestamp)
                   if _timestamp < comparetimestamp]

        # choose the max
        if indexes:
            position = max(indexes)

            # remove elements prior to that position
            self._removeBufferAtPosition(position)

    def _removeBufferAtPosition(self, position):

        del self._systemtimestamp[:position]
        del self._timestamp[:position]
        del self._uptime[:position]
        del self._score[:position]
        del self._gender[:position]
        del self._surprised[:position]
        del self._sad[:position]
        del self._happy[:position]
        del self._angry[:position]
        del self._age[:position]
        del self._mouthOpen[:position]
        del self._leftEyeClosed[:position]
        del self._rightEyeClosed[:position]
        del self._laughState[:position]

    def isCloseTo(self, frame):

        midX, midY = self.frame.center()
        midXframe, midYframe = frame.center()

        return (abs(midX - midXframe) < 200 and
                abs(midY - midYframe) < 200)

    def uptime(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._uptime[-1]

    def score(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._score[-1]

    def gender(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._gender[-1]

    def surprised(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._surprised[-1]

    def sad(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        filtered = filter(lambda x: x is not None, self._sad)
        return numpy.mean(filtered)

    def happy(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        filtered = filter(lambda x: x is not None, self._happy)
        return numpy.mean(filtered)

    def angry(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        filtered = filter(lambda x: x is not None, self._angry)
        return numpy.mean(filtered)

    def age(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        filtered = filter(lambda x: x is not None, self._age)
        return numpy.mean(filtered)

    def mouthOpen(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        filtered = filter(lambda x: x is not None, self._mouthOpen)
        return numpy.mean(filtered)

    def leftEyeClosed(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._leftEyeClosed[-1]

    def rightEyeClosed(self):

        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._rightEyeClosed[-1]
        
    def laughState(self):
        
        # check if it should remove items from the buffer
        self._checkTimeStamp()

        return self._laughState[-1]


class Frame:
    '''Frame class'''

    def __init__(self, left, top, right, bottom):

        # save the properties
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def width(self):
        return self.right - self.left

    def height(self):
        return self.bottom - self.top

    def center(self):

        # calculate middle point of X and Y
        midX = self.left + self.width() / 2
        midY = self.top + self.height() / 2

        # Calibration
        #print "(" + str(midX) + ", " + str(midY) + ")"

        return midX, midY


''' main '''
if __name__ == '__main__':

    # define the callback functions       
    def laughStart():
        print datetime.now().strftime("%M:%S") + " laughStart called"
        
    def laughStop():
        print datetime.now().strftime("%M:%S") + " laughStop called"

    # init the Audience Analyser with X people audience
    analyser = AudienceAnalyser(11, laughStart, laughStop)

    # start the analyser and wait for a connection
    analyser.start()
