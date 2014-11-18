# imported first so that import puts ryu on sys path.
from openflow_util import (
    generate_add_flowmod, generate_barrier, generate_config_request)

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


class WriteThroughManagerTest(TestClass):

    def test_name(self):
        return 'WriteThroughManager'
    
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
        
        write_through_manager = WriteThroughMessageManager(
            incoming_sdn_socket,outgoing_socket_manager)
        write_through_manager.start_service()

        #### CHECK THAT WE CAN DESERIALIZE FLOWMODS #####
        
        # write a flowmod into incoming_sdn_socket
        written_sdn_message = generate_add_flowmod()        
        written_sdn_message.serialize()
        incoming_sdn_socket.write_into_read(written_sdn_message.buf)
        
        # read sdn message from output
        read_sdn_message = (
            outgoing_sdn_message_reader.blocking_read_sdn_message())

        # check that read sdn message is same as sent.  Using strs
        # here because messages don't have clean overridden equals
        if str(written_sdn_message) != str(read_sdn_message):
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

        if read_config_request.buf != config_request_to_send.buf:
            return False
        
        return True
