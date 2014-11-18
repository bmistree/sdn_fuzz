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
from sdn_fuzz.message_manager.reverse_flowmods_message_manager import (
    ReverseFlowmodsMessageManager)

class ReverseManagerTest(TestClass):
    '''
    Issue many flow mods, followed by a barrier.  Check that get the
    flowmods back in reverse.
    '''
    
    def test_name(self):
        return 'ReverseFlowmodsManager'
    
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
        
        write_through_manager = ReverseFlowmodsMessageManager(
            incoming_sdn_socket,outgoing_socket_manager)
        write_through_manager.start_service()
        

        #### CHECK THAT FLOWMODS ACTUALLY ARRIVE BACKWARDS #####
        NUM_FLOWMODS_TO_SEND = 50
        
        # Send 50 flow mods, then a barrier.
        send_flowmod_list = []
        for i in range(0,NUM_FLOWMODS_TO_SEND):
            flowmod_to_send = generate_add_flowmod(i)
            flowmod_to_send.serialize()
            send_flowmod_list.append(flowmod_to_send)
            incoming_sdn_socket.write_into_read(flowmod_to_send.buf)


        # send a barrier
        barrier_to_send = generate_barrier()
        barrier_to_send.serialize()
        incoming_sdn_socket.write_into_read(barrier_to_send.buf)
        
        for sent_flowmod in reversed(send_flowmod_list):
            # read sdn message from output
            read_sdn_message = (
                outgoing_sdn_message_reader.blocking_read_sdn_message())

            if str(read_sdn_message) != str(sent_flowmod):
                return False

        # check that also received final barrier
        read_barrier = (
            outgoing_sdn_message_reader.blocking_read_sdn_message())
        if type(read_barrier) != type(barrier_to_send):
            return False
            
        return True
