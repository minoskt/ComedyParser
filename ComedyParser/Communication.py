#!/usr/bin/env python

import sys
import socket
import time
import threading
import xml.etree.ElementTree as ET
import Command
from datetime import datetime
from Robot import Robot
from RobotMapping import RobotMapping


class CommunicationModule:
    """CommunicationModule Class"""

    def __init__(self, ip, port=7766):

        # init RobotMapping with calibration.json file
        self._robotMapping = RobotMapping("calibration_template.json")

        # init socket
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # init connected
        self.connected = False

        # save ip and port
        self._ip = ip
        self._port = port

        # create keep-alive command
        self._keepAliveCommand = Command.CommandKeepAlive()

        # create read thread
        self._read_thread = threading.Thread(target=self.read, args=())
        self._read_thread.daemon = True

        # init Callback Stacks
        self._tts_stop_callback_stack = []
        self._seq_stop_callback_stack = []

        # init Callback dics
        self._read_output_callback_dic = {}
        self._read_output_callback_parameter_dic = {}

    def connect(self):

        # open connection
        self._s.connect((self._ip, self._port))
        self.connected = True

        # start the thread
        self._read_thread.start()

        # Authorise (access_level, user, password)
        authCommand = Command.CommandAuth('3', 'flash', 'foobar')
        self.send(authCommand)

        # subscribe to the required notifications
        self._subscribeToNotifications()

        # Enable thread for keep-alive command
        self.setKeepAliveEnabled(True)

    def disconnect(self):

        # set as disconnected
        self.connected = False

        # Disable thread for keep-alive command
        self.setKeepAliveEnabled(False)

        # close connection
        self._s.close()

    def setKeepAliveEnabled(self, enabled):

        if enabled:
            self._keepAlive = True
            self._sendKeepAlive()
        else:
            self._keepAlive = False

    def _sendKeepAlive(self):

        if self._keepAlive:

            # schedule for the next call in 4 sec
            threading.Timer(4.0, self._sendKeepAlive).start()

            # send the command
            self.send(self._keepAliveCommand, False)

    def _subscribeToNotifications(self):

        # TTS Stop
        subsCommand = Command.CommandSubscribe(
            'input_management', 'entity_value', '170')

        self.send(subsCommand)

        # Sequence Stoped
        subsCommand = Command.CommandSubscribe(
            'sequence_management', 'function', '3')

        self.send(subsCommand)

    def send(self, command, debug=True):

        # DEBUG: print the command
        #if debug is True:
        #    print '-------'
        #    print 'Command:'
        #    print command.message

        if self.connected:
            # send the command (with '\0' at the end)
            self._s.send(command.message + '\0')

    def read(self):

        # while you are connected
        while self.connected:

            data = self._s.recv(2048)

            # DEBUG: print the response
            #if not 'keep_alive' in data:
            #    print '-------'
            #    print 'Response:'
            #    print data

            # filter data with empty string
            if len(data) > 1:

                # get the data and break them into multiple xml parts
                xmldatalist = self.convertResponseToList(data)

                # iterate through all parts
                for xmldata in xmldatalist:

                    # Parse the response
                    if len(xmldata) > 1:
                        self.parseResponse(xmldata)

    def convertResponseToList(self, data):

        # create  an empty list
        xmldatalist = []

        # that's the endstring that we want to split after
        endstring = "</ioxts>"

        # init the search
        position = data.find(endstring)

        # while we can't find any other substring
        while position != -1:

            # calculate the end position
            endposition = position + len(endstring)

            # find the substring
            xmlstring = data[:endposition]

            # append it to the lsit
            xmldatalist.append(xmlstring.strip())

            # remove this part from the data
            data = data[endposition:]

            # find the next position
            position = data.find(endstring)

        # return the list
        return xmldatalist

    def parseResponse(self, xmldata):

        # debug
        #print "---------------------"
        #print xmldata
        #print "---------------------"

        # Check for input_management notification
        #if (xmldata.find("<notification>") != -1 and
        #        xmldata.find("<object>input_management</object>") != -1 and
        #        xmldata.find("<input_id>170</input_id>") != -1 and
        #        xmldata.find("<value>stopped</value>") != -1):

            #self.tts_stop_callback()

        # Check for sequence_management notification
        if (xmldata.find("<notification>") != -1 and
                xmldata.find("<object>sequence_management</object>") != -1):
                # Important: Add more checks here to avoid
                #            problems in the future

            if self._seq_stop_callback_stack:
                callback_structure = self._seq_stop_callback_stack.pop()
                callback = callback_structure["callback"]

                #print "SEQ STOP   ---   " + str(datetime.now().time())

                # call the callback function
                if callback is not None:
                    callback()

        elif (xmldata.find("<response>") != -1 and
                xmldata.find("<object>output_management</object>") != -1 and
                xmldata.find("<function_name>read</function_name>") != -1):

            # get the values
            requestor_id = self.readParameter(xmldata, 'requestor_id')
            value = self.readParameter(xmldata, 'value')

            # call the callback
            if requestor_id in self._read_output_callback_dic.keys():

                parameter = self._read_output_callback_parameter_dic[requestor_id]

                self._read_output_callback_dic[requestor_id](parameter, value)

                # remove callbacks
                del self._read_output_callback_dic[requestor_id]
                del self._read_output_callback_parameter_dic[requestor_id]

            else:
                print "WARNING: Requestor id '%s' doesnt exist in callback list" % (requestor_id)

    def readParameter(self, xmldata, parameter):

        # I'm really sorry for this code....

        lines = xmldata.splitlines( );

        for line in lines:
            if line.find("<"+parameter+">") != -1:
                line = line.strip()
                line = line.replace("<"+parameter+">", "")
                line = line.replace("</"+parameter+">", "")
                return line

        return None

    def tts_stop_callback(self):
        if self._tts_stop_callback_stack:
                callback_structure = self._tts_stop_callback_stack.pop()
                callback = callback_structure["callback"]

                #print "TTS STOP   ---   " + str(datetime.now().time())
                #print "text was: " + callback_structure["text"]
                #print xmldata

                # call the callback function
                if callback is not None:
                    callback()

    def say(self, text, voice=None, stop_callback=None):

        # say it!
        sayCommand = Command.CommandSay(text, voice)
        self.send(sayCommand)

        # save the callback for later call
        callback_structure = {"text": text,
                              "voice": voice,
                              "callback": stop_callback}

        # push it to the stack
        self._tts_stop_callback_stack.append(callback_structure)

    def play(self, filename):

        # play it!
        playCommand = Command.CommandPlay(filename)
        self.send(playCommand)

    def sequence(self, command, sequence, stop_callback=None):
        ''' sequence management
            command can be: play, pause, stop ...
            seq_stoped_callback can only be used for play command'''

        # send the seq command
        seqCommand = Command.CommandSequenceManagement(sequence, command)
        self.send(seqCommand)

        # save the callback for later call
        callback_structure = {"command": command,
                              "sequence": sequence,
                              "callback": stop_callback}

        # push it to the stack
        self._seq_stop_callback_stack.append(callback_structure)

    def controlfunction_enable(self, function, active=True):

        # send the control function enable command
        command = Command.CommandFunctionEnable(function, active)
        self.send(command)

    def controlfunction_setvariables(self, function, vardict):

        # send the control function set var command
        command = Command.CommandFunctionSet(function, vardict)
        self.send(command)

    def look(self, x, y):

        # get the mapped values for x, y
        outputs = self._robotMapping.look(x, y)

        # send the command
        self.command_sequence(outputs)

    def point(self, x, y):

        # get the mapped values for x, y
        outputs = self._robotMapping.point(x, y)

        # send the command
        self.command_sequence(outputs)

    def pointreset(self):

        # get the point reset values
        outputs = self._robotMapping.pointreset()

        # send the command
        self.command_sequence(outputs)

    def pointBackLeft(self):

        # get the point reset values
        outputs = self._robotMapping.pointBackLeft()

        # send the command
        self.command_sequence(outputs)

    def command_sequence(self, dic):

        for key in dic.keys():
            command = Command.CommandOutput(key, dic[key])
            self.send(command)

    def command_output_read(self, parameter, output_id, callback):

        # prepare the command
        command = Command.CommandOutputRead(output_id)

        # save the callback with requestor_id
        requestor_id = command.requestor_id
        self._read_output_callback_dic[requestor_id] = callback
        self._read_output_callback_parameter_dic[requestor_id] = parameter

        # send the command
        self.send(command)


''' main '''
if __name__ == '__main__':

    # init communication module
    comm = CommunicationModule('192.168.32.2', 7766)

    # connect, auth and start keep-alive thread
    comm.connect()

    # just wait one sec
    time.sleep(1)

    # ------------------------------------------------

    # Callback for when the TTS ends
    def callback():
        print 'OK, done!'

    # Say something with Simon's voice. Callback at the end
    #comm.say('Hello! Test 1 2 3. Test!', 'Simon', callback)

    # ------------------------------------------------

    def callback(parameter, value):
        print parameter + " = " + value

    comm.command_output_read('param', '87', callback)

    # Don't disconnect imidiately
    time.sleep(1)

    # stop keep-alive thread and disconnect
    comm.disconnect()
