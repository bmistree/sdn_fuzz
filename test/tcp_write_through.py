# imported first so that import puts ryu on sys path.
from openflow_util import (
    generate_add_flowmod, generate_barrier, generate_config_request)

import socket
import os
import sys
import time

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),'..','ryu_extend'))
import additional_parsers


sdn_fuzz_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(sdn_fuzz_folder)

from test_class import TestClass


from sdn_fuzz.sdnsocket.tcp_sdnsocket import TCPSDNSocket

from sdn_fuzz.sdn_message_reader import SDNMessageReader
from sdn_fuzz.message_manager.write_through_message_manager import (
    WriteThroughMessageManager)


SWITCH_CONNECTING_TO_PORT = 45306
CONTROLLER_PORT = SWITCH_CONNECTING_TO_PORT + 1

import Queue # using as an mvar
import threading
def start_listening(port_to_listen_on):
    mvar = Queue.Queue()
    
    def internal_thread():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('0.0.0.0',port_to_listen_on))
        s.listen(1)
        sock, _ = s.accept()
        mvar.put(sock)

    t = threading.Thread(target=internal_thread)
    t.setDaemon(True)
    t.start()
    # wait a short period of time to insure that internal thread is
    # scheduled.
    time.sleep(1)
    return mvar

    
NUM_FLOWMODS_TO_SEND = 20

class TCPWriteThroughTest(TestClass):

    def __init__(self):
        '''
        '''

    def test_name(self):
        return 'TCPWriteThroughTest'
        
    def run_test(self):
        '''
        @returns {boolean} --- True if test passed, false otherwise.

        [Switch]--->switch_to_interposition_socket
                --->switch_incoming_interposition_socket-->[Interposition]


        [Interposition]--->interposition_to_controller_socket
                       --->controller_incoming_socket
        '''
        # switch to interposition setup
        switch_incoming_interposition_socket_mvar = (
            start_listening(SWITCH_CONNECTING_TO_PORT))
        
        switch_to_interposition_socket = (
            socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        switch_to_interposition_socket.connect(
            ('0.0.0.0',SWITCH_CONNECTING_TO_PORT))

        switch_incoming_interposition_socket = (
            switch_incoming_interposition_socket_mvar.get())

        # interposition to controller setup
        controller_incoming_socket_mvar = start_listening(CONTROLLER_PORT)
        
        interposition_to_controller_socket = (
            socket.socket(socket.AF_INET, socket.SOCK_STREAM))
        interposition_to_controller_socket.connect(
            ('0.0.0.0',CONTROLLER_PORT))

        
        controller_incoming_socket = controller_incoming_socket_mvar.get()
        
        # make sdn sockets
        sdn_switch_to_interposition_socket = TCPSDNSocket(
            switch_to_interposition_socket)
        sdn_switch_incoming_interposition_socket = TCPSDNSocket(
            switch_incoming_interposition_socket)
        sdn_interposition_to_controller_socket = TCPSDNSocket(
            interposition_to_controller_socket)
        sdn_controller_incoming_socket = TCPSDNSocket(
            controller_incoming_socket)

        # switch to controller manager: do not do any reordering in
        # either direction.

        # switch ---switch_to_controller_manager---> controller
        # controller <---controller_to_switch_manager--- switch
        switch_to_controller_manager = WriteThroughMessageManager(
            sdn_switch_incoming_interposition_socket,
            sdn_interposition_to_controller_socket)
        controller_to_switch_manager = WriteThroughMessageManager(
            sdn_interposition_to_controller_socket,
            sdn_switch_incoming_interposition_socket)

        switch_to_controller_manager.start_service()
        controller_to_switch_manager.start_service()
        

        # write into sdn_switch_to_interposition_socket and try to
        # read it out of sdn_controller_incoming_socket.
        message_sent_list = []
        for i in range(0,NUM_FLOWMODS_TO_SEND):
            flowmod_to_send = generate_add_flowmod(i)
            flowmod_to_send.serialize()
            sdn_switch_to_interposition_socket.write(flowmod_to_send.buf)
            message_sent_list.append(flowmod_to_send)
            
        # read messages.  check if messages agree
        sdn_message_reader = SDNMessageReader(sdn_controller_incoming_socket)
        for i in range(0,NUM_FLOWMODS_TO_SEND):
            flowmod_received = sdn_message_reader.blocking_read_sdn_message()
            flowmod_received.serialize()
            if message_sent_list[i].buf != flowmod_received.buf:
                return False

        return True
