# imported first so that import puts ryu on sys path.
from openflow_util import (
    generate_add_flowmod, generate_barrier, generate_config_request,
    generate_switch_features_buffer)

import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),'..','ryu_extend'))
import additional_parsers


sdn_fuzz_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(sdn_fuzz_folder)

from test_class import TestClass
from sdn_fuzz.sdnsocket.manual_sdnsocket import ManualSDNSocket
from sdn_fuzz.sdnsocket.crossover_manual_sdn_socket import (
    crossover_manual_sdn_socket)

from sdn_fuzz.sdn_message_reader import SDNMessageReader
from sdn_fuzz.message_manager.write_through_message_manager import (
    WriteThroughMessageManager)

NUM_WRITES=25

class WriteThroughManagerBase(TestClass):

    def __init__(self,write_through_message_manager_class):
        '''
        Should take in two sdnsockets to initialize a class: first
        socket is socket listening on, second socket is socket sending
        to.
        '''
        self.write_through_message_manager_class = (
            write_through_message_manager_class)


    def run_test(self):
        '''
        @returns {boolean} --- True if test passed, false otherwise.
        '''

        # incoming_socket ---> Manager ---> outgoing_socket
        incoming_sdn_socket = ManualSDNSocket()
        # outgoing_socket above gets written by outgoing_socket_manager
        # and read from outgoing_socket_switch
        (outgoing_socket_manager,outgoing_socket_switch) = (
            crossover_manual_sdn_socket())

        outgoing_sdn_message_reader = SDNMessageReader(outgoing_socket_switch)
        write_through_manager = self.write_through_message_manager_class(
            incoming_sdn_socket,outgoing_socket_manager)
        write_through_manager.start_service()

        #### CHECK THAT WE CAN DESERIALIZE FLOWMODS #####
        for i in range(0,NUM_WRITES):
            # write a flowmod into incoming_sdn_socket
            written_sdn_message = generate_add_flowmod(i)
            written_sdn_message.serialize()
            incoming_sdn_socket.write_into_read(written_sdn_message.buf)

            # read sdn message from output
            read_sdn_message = (
                outgoing_sdn_message_reader.blocking_read_sdn_message())

            # check that read sdn message is same as sent.  Using strs
            # here because messages don't have clean overridden equals
            if written_sdn_message.buf != read_sdn_message.original_buffer:
                return False

        #### CHECK THAT WE CAN DESERIALIZE BARRIERS #####
        barrier_to_send = generate_barrier()
        barrier_to_send.serialize()
        incoming_sdn_socket.write_into_read(barrier_to_send.buf)

        read_barrier = (
            outgoing_sdn_message_reader.blocking_read_sdn_message())
        if type(read_barrier) != type(barrier_to_send):
            return False
        

        #### CHECK THAT WE CAN CORRECTLY DESERIALIZE OTHER MESSAGES #####
        config_request_to_send = generate_config_request()
        config_request_to_send.serialize()
        incoming_sdn_socket.write_into_read(config_request_to_send.buf)
        
        # should be of type additional_parsers.UnparsedMessage
        read_config_request = (
            outgoing_sdn_message_reader.blocking_read_sdn_message())

        if read_config_request.original_buffer != config_request_to_send.buf:
            return False


        # send a bunch of switch features.
        NUM_GENERATE_SWITCH_FEATURES_TO_WRITE = 10
        switch_features_buffer_list = []
        for i in range(0,NUM_GENERATE_SWITCH_FEATURES_TO_WRITE):
            buf_to_write = generate_switch_features_buffer()
            incoming_sdn_socket.write_into_read(buf_to_write)
            switch_features_buffer_list.append(buf_to_write)

        for i in range(0,10):
            read_config_request = (
                outgoing_sdn_message_reader.blocking_read_sdn_message())
            read_config_request.serialize()
            
            if switch_features_buffer_list[i] != read_config_request.buf:
                return False
        
        return True


class WriteThroughManagerTest(WriteThroughManagerBase):
    def __init__(self):
        super(WriteThroughManagerTest,self).__init__(WriteThroughMessageManager)
        
    def test_name(self):
        return 'WriteThroughManager'
    
