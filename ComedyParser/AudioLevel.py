#!/usr/bin/env python

# This module requires PyAudio (python bindings of PortAudio lib)
# http://people.csail.mit.edu/hubert/pyaudio/

import sys
import time
import pyaudio
import audioop
import threading

# constants
FORMAT = pyaudio.paInt16
DEFAULT_BLOCK_TIME = 0.05


class AudioLevelModule:
    '''An AudioLevelModule class'''

    def __init__(self, callback, delay=0.1, device_index=None):

        # save the callback and the delay
        self._callback = callback
        self._device_index = device_index
        self.delay = delay

        # init started
        self._started = False

        # init AudioLevelReader
        self._audioLevelReader = AudioLevelReader(device_index)

    def all_streams(self):

        # return all streams
        return self._audioLevelReader.all_streams()

    def start(self):

        # set as started
        self._started = True

        # start the reader
        self._audioLevelReader.start()

        # initiate the read
        self._read()

    def stop(self):

        # stop the reader
        self._audioLevelReader.stop()

        # set as stopped
        self._started = False

    def _read(self):

        # only if started
        if self._started:

            # get the level
            level = self._audioLevelReader.volume()

            # call with volume
            if level is not None:
                self._callback(level)

            # schedule for the next call in self.delay sec
            threading.Timer(self.delay, self._read).start()


class AudioLevelReader(threading.Thread):
    '''An AudioLevelReader class'''

    def __init__(self, device_index=None):

        # call the super init for threading
        super(AudioLevelReader, self).__init__()

        # init PyAudio engine
        self._p = pyaudio.PyAudio()

        # set stream as None
        self._stream = None

        # save the device_index
        self._device_index = device_index

        # init the buffer
        self._buffer = []

        # set running to False
        self._running = False

    def all_streams(self):

        streams = []

        for i in range(self._p.get_device_count()):
            device_info = self._p.get_device_info_by_index(i)
            streams.append(device_info['name'])

        return streams

    def _open(self):

        # get the device_index
        device_index = self._device_index

        if device_index is None:
            default_input = self._p.get_default_input_device_info()
            device_index = default_input['index']

        elif device_index not in range(self._p.get_device_count()):
            sys.exit('Error: device_index is invalid.')

        # else get the device info
        device_info = self._p.get_device_info_by_index(device_index)

        self._channels = device_info['maxInputChannels']
        self._rate = int(device_info['defaultSampleRate'])
        self._input_frames_per_block = int(self._rate * DEFAULT_BLOCK_TIME)

        # open the stream
        stream = self._p.open(format=FORMAT,
                              channels=self._channels,
                              rate=self._rate,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=self._input_frames_per_block)

        self._stream = stream

    def _read(self):

        if self._stream:
            try:
                block = self._stream.read(self._input_frames_per_block)
            except IOError, e:
                # print error
                print 'Error: ' + e.errno
                return -1

        else:
            print 'Error: input stream is not open'
            return -1

        # calculate the amplitude
        amplitude = audioop.rms(block, 2)

        return amplitude

    def _close(self):

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        else:
            print 'Error: input stream is not open'

    def run(self):

        # open the stream
        self._open()

        # set running flag
        self._running = True

        # while it is running
        while self._running:

            # add the volume to the buffer
            _volume = self._read()
            self._buffer.append(_volume)

        # set the volume to None once it is stopped
        self._volume = None

    def stop(self):

        # set the flag so that run returns
        self._running = False

    def volume(self):

        # if the buffer is not empty
        if self._buffer:

            # find the average
            avg = sum(self._buffer)/len(self._buffer)

            # empty the list
            del self._buffer[:]

            # return the avg
            return avg

        else:
            return None


''' main '''
if __name__ == '__main__':

    def printLevel(level):
        print level

    # init the AudioLevelModule with callback and default delay
    audioModule = AudioLevelModule(printLevel, 0.1, 1)

    # print all available devices
    print 'Available devices:'

    for index, stream in enumerate(audioModule.all_streams()):
        print('%d. %s' % (index, stream))

    print '-------------------'

    # start
    audioModule.start()

    # wait 10 secs
    time.sleep(500)

    # stop
    audioModule.stop()
