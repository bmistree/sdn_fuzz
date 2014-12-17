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

from sdn_fuzz.message_manager.uniform_prob_error_message_manager import (
    UniformProbErrorMessageManager)

from test_class import TestClass
from sdn_fuzz.sdnsocket.manual_sdnsocket import ManualSDNSocket
from sdn_fuzz.sdn_message_reader import SDNMessageReader

NUM_WRITES = 500

class ErrorManagerAllErrorsTest(TestClass):

    def __init__(self):
        super(ErrorManagerAllErrorsTest,self).__init__()
        
    def test_name(self):
        return 'ErrorManagerAllErrors'
    
    def run_test(self):
        '''
        @returns {boolean} --- True if test passed, false otherwise.
        '''
        # incoming_socket ---> Manager ---> dummy_sdn_socket
        incoming_sdn_socket = ManualSDNSocket(True)
        dummy_sdn_socket = ManualSDNSocket()

        all_errors_message_manager = UniformProbErrorMessageManager(
            1.0,incoming_sdn_socket,dummy_sdn_socket)
                                                                    
        all_errors_message_manager.start_service()

        #### CHECK THAT WE CAN DESERIALIZE FLOWMODS #####
        
        # write a set of flow mods to other side
        for i in range(0,NUM_WRITES):
            written_sdn_message = generate_add_flowmod()        
            written_sdn_message.serialize()
            incoming_sdn_socket.write_into_read(written_sdn_message.buf)

        incoming_sdn_socket_reader = SDNMessageReader(incoming_sdn_socket)
        for i in range(0,NUM_WRITES):
            read = (
                incoming_sdn_socket_reader.blocking_read_sdn_message(True))
        
        return True

