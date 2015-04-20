# imported first so that import puts ryu on sys path.
from openflow_util import (
    generate_add_flowmod, generate_barrier, generate_config_request)

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
from sdn_fuzz.sdnsocket.manual_sdnsocket import ManualSDNSocket
from sdn_fuzz.sdnsocket.crossover_manual_sdn_socket import (
    crossover_manual_sdn_socket)

from sdn_fuzz.sdn_message_reader import SDNMessageReader
from sdn_fuzz.message_manager.timed_reverse_flowmods_message_manager import (
    TimedReverseFlowmodsMessageManager)

SEND_BUFFER_AFTER_SECONDS = 5.

class TimedReverseManagerTest(TestClass):
    '''
    Issue many flow mods, without any barrier.  Check to ensure that
    they eventually get sent.
    '''
    
    def test_name(self):
        return 'TimedReverseFlowmodsManager'
    
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
        
        write_through_manager = TimedReverseFlowmodsMessageManager(
            SEND_BUFFER_AFTER_SECONDS,incoming_sdn_socket,
            outgoing_socket_manager)
        write_through_manager.start_service()
        

        #### SEND FLOWMODS #####
        NUM_FLOWMODS_TO_SEND_PER_BATCH = 50

        
        # Send 50 flow mods, wait, then send another batch.  Check if
        # get two separate buffers backwards.
        send_flowmod_list_batch_one = []
        for i in range(0,NUM_FLOWMODS_TO_SEND_PER_BATCH):
            flowmod_to_send = generate_add_flowmod(i)
            flowmod_to_send.serialize()
            send_flowmod_list_batch_one.append(flowmod_to_send)
            incoming_sdn_socket.write_into_read(flowmod_to_send.buf)


        # wait before sending another round of flowmods
        time.sleep(SEND_BUFFER_AFTER_SECONDS * 2)

        # second flowmod batch
        send_flowmod_list_batch_two = []
        for i in range(0,NUM_FLOWMODS_TO_SEND_PER_BATCH):
            flowmod_to_send = generate_add_flowmod(i)
            flowmod_to_send.serialize()
            send_flowmod_list_batch_two.append(flowmod_to_send)
            incoming_sdn_socket.write_into_read(flowmod_to_send.buf)

        # wait before sending another round of flowmods
        time.sleep(SEND_BUFFER_AFTER_SECONDS * 2)


        # third flowmod batch should be sent in order because we insert barriers.
        send_flowmod_or_barrier_list_batch_three = []
        for i in range(0,NUM_FLOWMODS_TO_SEND_PER_BATCH):
            flowmod_to_send = generate_add_flowmod(i)
            flowmod_to_send.serialize()
            send_flowmod_or_barrier_list_batch_three.append(flowmod_to_send)
            incoming_sdn_socket.write_into_read(flowmod_to_send.buf)

            # send a barrier
            barrier_to_send = generate_barrier()
            barrier_to_send.serialize()
            incoming_sdn_socket.write_into_read(barrier_to_send.buf)
            send_flowmod_or_barrier_list_batch_three.append(barrier_to_send)

            
        #### CHECK FLOWMODS ARRIVE IN CORRECT ORDER #####
        # read all batches of flowmods and check that they arrive in
        # correct order: first batch should be reversed; second batch
        # should also be in reverse; third should not be reversed.

        # first batch should be reversed
        for sent_flowmod in reversed(send_flowmod_list_batch_one):
            # read sdn message from output
            read_sdn_message = (
                outgoing_sdn_message_reader.blocking_read_sdn_message())

            if read_sdn_message.original_buffer != sent_flowmod.buf:
                return False
            
        # second batch should be reversed
        for sent_flowmod in reversed(send_flowmod_list_batch_two):
            # read sdn message from output
            read_sdn_message = (
                outgoing_sdn_message_reader.blocking_read_sdn_message())

            if read_sdn_message.original_buffer != sent_flowmod.buf:
                return False
            
        # third batch should be in order
        for sent_flowmod_or_barrier in send_flowmod_or_barrier_list_batch_three:
            # read sdn message from output
            read_sdn_message = (
                outgoing_sdn_message_reader.blocking_read_sdn_message())

            if read_sdn_message.original_buffer != sent_flowmod_or_barrier.buf:
                return False

            
        return True
