#!/usr/bin/env python

import sys
import time
from datetime import datetime
from AudioLevel import AudioLevelModule

# constants
DEFAULT_MIN_TIME = 0.5
DEFAULT_MAX_TIME = 1

# enums
QUIET_STATE = 0
LOUD_STATE = 1


class TriggerModule:
    '''A Trigger Module class'''

    def __init__(self,
                 start_callback,
                 stop_callback,
                 threshold,
                 min_time=DEFAULT_MIN_TIME,
                 max_time=DEFAULT_MAX_TIME):

        # save callback functions
        self._start_callback = start_callback
        self._stop_callback = stop_callback

        # set init properties
        self.min_time = min_time
        self.max_time = max_time

        self._loudTimestamp = None
        self._quietTimestamp = None

        self.threshold = threshold

        self._last_state = QUIET_STATE

    def monitorLevel(self, level):

        if (level >= 0):  # no error

            if (level > self.threshold and
                    self._last_state == QUIET_STATE):

                if self._loudTimestamp is None:
                    self._loudTimestamp = datetime.now()

                self._quietTimestamp = None

                deltatime = datetime.now() - self._loudTimestamp

                #print "Loud: %.2f" % (deltatime.total_seconds())

                if (deltatime.total_seconds() >= self.max_time):

                    # set last state to loud
                    self._last_state = LOUD_STATE

                    # call the start callback
                    self._start_callback()

            elif (level <= self.threshold and  # quiet
                    self._last_state == LOUD_STATE):

                if self._quietTimestamp is None:
                    self._quietTimestamp = datetime.now()

                self._loudTimestamp = None

                deltatime = datetime.now() - self._quietTimestamp

                print "Quiet: %.2f" % (deltatime.total_seconds())

                if (deltatime.total_seconds() >= self.min_time):

                    # set last state to quiet
                    self._last_state = QUIET_STATE

                    # call the stop callback
                    self._stop_callback()

            else:
                self._loudTimestamp = None
                self._quietTimestamp = None


def triggerStartFunction():
    print "--- Start!"


def triggerStopFunction():
    print "--- Stop!"


''' main '''
if __name__ == '__main__':

    def volumeCallback(level):
        triggerModule.monitorLevel(level)
        # print level  # DEBUG

    # delay for the audioModule
    delay = 0.01

    # init the AudioLevelModule with given callback and delay
    audioModule = AudioLevelModule(volumeCallback, delay)

    # just use an example threshold of 400
    threshold = 100

    # init the TriggerModule with a callback function
    triggerModule = TriggerModule(triggerStartFunction,
                                  triggerStopFunction,
                                  threshold)

    # open the default stream of the AudioLevelModule
    audioModule.start()

    # wait 30 secs
    time.sleep(30)

    # close the stream of the AudioLevelModule
    audioModule.stop()
