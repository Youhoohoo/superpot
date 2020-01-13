#!/usr/bin/env python
# encoding: utf-8

import socket
import string
import hpfeeds

class HPFhandler(object):
    def __init__(self, host, port, ident, secret, channels):
        self.host = host
        self.port = port
        self.ident = ident
        self.secret = secret
        self.channels = channels
        self.max_retires = 5
        self._initial_connection_happend = False

    def _start_connection(self):
        self.hpc = hpfeeds.new(self.host, self.port, self.ident, self.secret)
        self._initial_connection_happend = True

    def feeddata(self, data):
        retries = 0
        if self._initial_connection_happend:
            while True:
                if retries >= self.max_retires:
                    break
                try:
                    self.hpc.publish(self.channels, data)
                except socket.error:
                    retries += 1
                    self.__init__(self.host, self.port, self.ident, self.secret, self.channels)
                else:
                    break
            error_msg = self.hpc.wait()
            return error_msg
        else:
            error_msg = "initial hpfeeds connect has not happend yet."
            return error_msg



if __name__ == '__main__':
    run = HPFhandler()
    run._start_connection()
