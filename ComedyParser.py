import sys
import time
import threading

from Comedy import Comedy
from Communication import CommunicationModule
from AudienceAnalyser import AudienceAnalyser

from datetime import datetime
from datetime import timedelta

from FileLogger import FileLogger


# audience size
expectedPeople = 45

# wait time for a response (in sec)
response_wait_time = 1.5

# max laugher time
max_laughter_counter = 4

# laughter_interval (in sec)
laughter_interval = 1

# max applauding time
max_applauding_time = 10


class ComedyParser(threading.Thread):
    """Joke Parser Class"""

    def __init__(self, comedy, ip, port=7766):

        # call the super init for threading
        super(ComedyParser, self).__init__()

        # parse comedy
        self._comedy = Comedy(comedy)

        # init FileLoger
        self._logger = FileLogger('log_ComedyParser')

        # init laughing and applauding flag
        self.laughing = None
        self.applauding = None
        self.laughter_counter = 0

        # Set initial after Response mode to NO.
        # This is used to check if the 1sec TTS gap is required
        self._afterResponse = False;

        # init the AudienceAnalyser
        self._audienceAnalyser = AudienceAnalyser(expectedPeople,
                                                  self._triggerStartFunction,
                                                  self._triggerStopFunction)

        # start the audience analyser
        self._audienceAnalyser.start()

        # init communication module
        self._communication = CommunicationModule(ip, port)

        # connect, auth and start keep-alive thread
        self._communication.connect()

        # generate all tokens in sentences
        self._tokenIterator = self._generateCombinedTokens()

        # init response iterator
        self._responseTokenIterator = None

    def _triggerStartFunction(self):
        ''' Trigger Started '''

        #print "---------- Trigger Started"

        # log it
        self._logger.log("Trigger Started")

        # set the laughing flag to ON
        self.laughing = datetime.now()

    def _triggerStopFunction(self):
        ''' Trigger Stopped '''

        #print "---------- Trigger Stopped"

        # log it
        self._logger.log("Trigger Stopped")

        # set the laughing flag to OFF
        self.laughing = None

    def _TTSEnded(self):
        '''TTS ended'''

        # sentence was delivered, continue the comedy
        self.continueComedy()

    def _PlayEnded(self):

        # Sound file play has been ended, continue the comedy
        self.continueComedy()

    def _SeqEnded(self):

        # Sequence play has been ended, continue the comedy
        self.continueComedy()

    def continueComedy(self):

        token = self._nextResponseToken()

        if token is None:
            token = self._nextToken()

            # a ref to the connected communication module
            #comm = self._communication

            # resume the motion
            #comm.sequence('resume', '8001')

        # play the next sentence
        self._playSentence(token)

    def _generateCombinedTokens(self):
        '''Generator of all sentences of the loaded comedy'''

        for joke in self._comedy.nextJoke():
            for line in joke.nextLine():
                for sentence in line.nextSentence():
                    for token in sentence.nextToken():
                        yield token

    def _generateResponses(self, line):
        '''Generator of all responses'''

        for sentence in line.nextSentence():
            for token in sentence.nextToken():
                yield token

    def _nextToken(self):
        '''Returns the next sentence'''

        try:
            self._current = next(self._tokenIterator)

        except StopIteration:
            self._current = None

        return self._currentToken()

    def _nextResponseToken(self):
        '''Returns the next response token'''

        if self._responseTokenIterator:

            try:
                self._currentResponse = next(self._responseTokenIterator)

            except StopIteration:
                self._currentResponse = None

            return self._currentResponseToken()

        else:
            return None

    def _currentToken(self):
        '''Returns the current sentence'''

        return self._current

    def _currentResponseToken(self):
        '''Returns the current sentence'''

        return self._currentResponse

    def _playSentence(self, token):
        ''' That's a really big method that checks the flow of the
            comedy and send the commands accordingly '''

        # a ref to the connected communication module
        comm = self._communication

        # Check the type of the token and send the command
        # None means Stop
        if token is not None:

            # for Text and Pause
            if token.tokentype in ['CombinedText', 'Pause']:

                # always wait one sec before a CombinedText
                # except if it is just after a response
                if self._afterResponse == False:
                    #print "Wait 1 sec"
                    time.sleep(1)
                    #print "Wait finished!"

                else:
                    # set it back to NO
                    self._afterResponse = False

                # get text
                text = token.getText()
                voice = self._comedy.tts_main_voice

                # send the say command
                comm.say(text, voice, self._TTSEnded)

                # log it
                self._logger.log("Saying '%s'" % (text))

            elif token.tokentype == 'Audio':

                # send the play command
                comm.play(token.filename)

                # log it
                self._logger.log("Playing audio '%s'" % (token.filename))

                # schedule the _PlayEnded call in X secs
                # unfortunatelly ios_serve doesn't notify you
                # thus, a callback cannot be implemented
                threading.Timer(token.length, self._PlayEnded).start()

            elif token.tokentype == 'Response':

                # log it
                self._logger.log("Wait for a response...")
                print "Wait for a response..."

                # wait for a response
                self.waitForResponse()

            elif token.tokentype == 'Command':

                # get the type of the command
                commandtype = token.commandType
                value = token.value
                refsave = token.refsave

                if commandtype == 'sequenceplay':

                    # send the sequence play command
                    comm.sequence('play', value)

                    # log it
                    self._logger.log("Playing sequence '%s'" % (value))

                    # continue immediately, we don't want to wait for the seq
                    # to finish before the next command since we only use it
                    # for movements and in parallel with TTS.
                    self.continueComedy()

                elif commandtype == 'sequencestop':

                    # send the sequence stop command
                    comm.sequence('stop', value)
                    comm.sequence('play', '2')

                    # log it
                    self._logger.log("Stopping sequence '%s'" % (value))

                    # continue immediately, we don't want to wait for the seq
                    # to finish before the next command since we only use it
                    # for movements and in parallel with TTS.
                    self.continueComedy()

                elif commandtype == 'look':

                    # find the person's coordinates
                    person = self.searchPeopleWithValue(value)

                    if person:
                        x, y = person.frame.center()

                        # call the look command of the communication object
                        comm.look(x, y)

                        # log it
                        self._logger.log('Looking at person %d (%d, %d)' % (person.id, x, y))

                        # in case there is a refsave
                        if refsave is not None:
                            self._audienceAnalyser.audience.savePerson(person,
                                                                       refsave)

                    # continue immediately, we don't want to wait for the
                    # control function to finish before the next command
                    # since we only use it for short movements and in parallel
                    # with TTS.
                    self.continueComedy()

                elif commandtype == 'point':

                    if value == 'reset':
                        comm.pointreset()

                        # log it
                        self._logger.log('Pointing reset')

                    elif value == 'backleft':
                        comm.pointBackLeft()

                        # log it
                        self._logger.log('Pointing to minos')

                    else:

                        # find the person's coordinates
                        person = self.searchPeopleWithValue(value)

                        if person:
                            x, y = person.frame.center()

                            # log it
                            self._logger.log('Pointing to person %d (%d, %d)' % (person.id, x, y))

                            # call the point AND look command of the
                            # communication object
                            comm.point(x, y)
                            comm.look(x, y)

                            # in case there is a refsave
                            if refsave is not None:
                                self._audienceAnalyser.audience.savePerson(
                                    person, refsave)

                    # continue immediately, we don't want to wait for the
                    # control function to finish before the next command
                    # since we only use it for short movements and in parallel
                    # with TTS.
                    self.continueComedy()

                else:
                    print "WARNING: Unknown commandtype: " + commandtype

            else:
                print 'WARNING: Unknown tokentype: ' + token.tokentype

    def waitForResponse(self):

        # a ref to the connected communication module
        comm = self._communication

        # TODO:
        # Play left/right eyes sequence

        # set after response mode to YES
        self._afterResponse = True;

        # wait 1.5 secs
        time.sleep(response_wait_time)

        # is the audience laughing?
        if self.laughing is None:

            # Negative response immediately:
            self._logger.log("Negative response")

            # get current token (should be Response)
            trigger = self._currentToken().trigger

            # get a response
            response = self._comedy.responses.getResponse("negative", trigger)

            # might be None, so check!
            if response is not None:

                # add items to the iterator
                self._responseTokenIterator = self._generateResponses(
                    response["response"])

            # continue comedy (but taking response in acount)
            self.continueComedy()

        else:

            # Do a positive gesture and look next random

            # Look to another person
            self.lookToRandomPerson()

            # wait interval
            time.sleep(laughter_interval)
            self.checkResponse()

    def checkResponse(self):

        # a ref to the connected communication module
        comm = self._communication

        # No Laughter identified
        if self.laughing is None:

            self._logger.log("No laughter any more, continuing")

            self.laughter_counter = 0

            # continue comedy (but taking response in acount)
            self.continueComedy()

        else:

            # increase laughter counter
            self.laughter_counter = self.laughter_counter + 1
            #print "Counter: " + str(self.laughter_counter)

            self._logger.log("Wait and increase counter")

            if self.laughter_counter == max_laughter_counter - 1:

                self.laughter_counter = 0
                #print "MAX - Possitive Response"

                self._logger.log("Max counter")

                # No more wait. Say a positive response sentence:

                # get current token (should be Response)
                trigger = self._currentToken().trigger

                # get a response
                response = self._comedy.responses.getResponse("positive",
                                                              trigger)

                # might be None, so check!
                if response is not None:

                    # add items to the iterator
                    self._responseTokenIterator = self._generateResponses(
                        response["response"])

                # continue comedy (but taking response in account)
                self.continueComedy()

            else:

                print "Look"

                # Look to another person
                self.lookToRandomPerson()

                # Wait and check again
                time.sleep(laughter_interval)
                self.checkResponse()

    def lookToRandomPerson(self):

        person = self.searchPeopleWithValue('random')

        if person:
            x, y = person.frame.center()

            # a ref to the connected communication module
            comm = self._communication

            # call the look command of the communication object
            comm.look(x, y)

            # log it
            self._logger.log('Looking at person %d (%d, %d)' % (person.id, x, y))

    def searchPeopleWithValue(self, value):

        if value == "happiest":
            people = self._audienceAnalyser.audience.getHappiestPerson()

        elif value == "unhappiest":
            people = self._audienceAnalyser.audience.getUnhappiestPerson()

        elif value == "male_happiest":
            audience = self._audienceAnalyser.audience
            people = audience.getHappiestPersonWithGender("Male")

        elif value == "female_happiest":
            audience = self._audienceAnalyser.audience
            people = audience.getHappiestPersonWithGender("Female")

        elif value == "youngest":
            audience = self._audienceAnalyser.audience
            people = audience.getYoungestPerson()

        elif value == "random":
            people = self._audienceAnalyser.audience.getRandomPerson()

        else:
            # should be a previously saved ref.
            people = self._audienceAnalyser.audience.getRefPerson(value)

            if people is None:
                print "WARNING: Couldn't find the ref: " + value

        return people

    def resume(self):

        #self.laughing = None
        #self.applauding = None
        print "Continue.."

    def laughing_on(self):

        self.laughing = datetime.now()
        print self.laughing.strftime('Laughing at %H:%M:%S.%f')

    def applauding_on(self):

        self.applauding = datetime.now()
        print self.applauding.strftime('Laughing at %H:%M:%S.%f')

    def lookAt(self, x, y):

        # a ref to the connected communication module
        comm = self._communication

        comm.look(x, y)

    def run(self):

        # DEBUG: Print the number of words of this comedy
        #print "Comedy Words:" + str(self._comedy.length())

        # start playing the comedy
        self._playSentence(self._nextToken())

        # Debug only
        #while True:
        #    time.sleep(1)

    def play(self):

        # if it hasn't already started
        if not self.isAlive():

            print datetime.now().strftime('Start Comedy at %H:%M:%S.%f')
            self._logger.log('Start Comedy')

            # start the comedy in this thread
            self.start()

        else:
            print "Comedy is already running"

    def stop(self):

        self._logger.log('Stop Comedy')

        # Don't disconnect imidiately
        time.sleep(1)

        # stop the analyser
        self._audienceAnalyser.stop()

        # stop keep-alive thread and disconnect
        self._communication.disconnect()

    def manual_tts_stop(self):

        self._communication.tts_stop_callback()
        self._logger.log('Manual TTS Stop')

''' main '''
if __name__ == '__main__':

    print "Use the command 'python playComedy.py input.json' to start ComedyParser"
