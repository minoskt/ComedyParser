#!/usr/bin/env python

import sys
import socket
import threading


class ReadShore(threading.Thread):
    ''' Read Shore data and pass them to the AudienceAnalyser '''

    def __init__(self, dataCallback, port=50007):

        # call the super init for threading
        super(ReadShore, self).__init__()

        # save the callback
        self._dataCallback = dataCallback

        # local host
        HOST = ''

        # init the socket server
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._s.bind((HOST, port))

    def run(self):

        print 'Listening for incoming connection...'

        # listen for a connection
        self._s.listen(1)
        conn, addr = self._s.accept()

        print 'Connected by', addr

        while True:

            # read the data
            data = conn.recv(2048)

            if not data:

                print "disconnected"

                conn.close()

                print "calling again"

                # listen for a connection
                self._s.listen(1)
                conn, addr = self._s.accept()

                print 'Connected by', addr

            else:
                # callback with the data
                #print data
                self._dataCallback(data)

            # send ok message
            conn.send("ok")
