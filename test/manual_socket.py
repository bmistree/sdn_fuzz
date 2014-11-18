import os
import sys
import time
from threading import Thread
from random import random

sdn_fuzz_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(sdn_fuzz_folder)

from test_class import TestClass
from sdn_fuzz.sdnsocket.manual_sdnsocket import ManualSDNSocket


class ManualSocketTest(TestClass):

    def test_name(self):
        return 'ManualSocketTest'
    
    def run_test(self):
        '''
        @returns {boolean} --- True if test passed, false otherwise.
        '''
        socket = ManualSDNSocket()

        # check if empty read returns empty array
        if len(socket.read(100)) != 0:
            return False

        # insert 100 bytes, and then read it, and ensure they're the
        # same.
        written_array = self._write_random_bytes(socket,100)
        read_array = socket.read(1000)
        if read_array != written_array:
            return False
        read_array = socket.read(1000)
        if len(read_array) != 0:
            return False

        # check if blocking read works: start a thread that delays and
        # then writes to a socket, and issue a blocking read.
        num_bytes_to_delayed_write = int(100 * random()) + 100
        t = Thread(
            target=self._delayed_write_random_bytes,
            args=(3,socket,num_bytes_to_delayed_write))
        t.setDaemon(True)
        t.start()
        read_array = socket.blocking_read(num_bytes_to_delayed_write)
        
        if len(read_array) != num_bytes_to_delayed_write:
            return False

        return True

    
    def _delayed_write_random_bytes(self,seconds_to_delay,
                                    socket,num_bytes_to_write):
        '''
        @param {int} seconds_to_delay --- Time to wait before writing
        random bytes.
        '''
        time.sleep(seconds_to_delay)
        return self._write_random_bytes(socket,num_bytes_to_write)

    
    def _write_random_bytes(self,socket,num_bytes_to_write):
        '''
        @returns {bytearray} --- What writing into socket
        '''
        to_write_array = bytearray(os.urandom(num_bytes_to_write))
        socket.write_into_read(to_write_array)
        return to_write_array
