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
from write_through_manager import WriteThroughManagerBase


def generate_no_error(incoming_sdn_socket,outgoing_socket):
    '''
    Should take in two sdnsockets to initialize a class: first
    socket is socket listening on, second socket is socket sending
    to.
    '''
    return UniformProbErrorMessageManager(
        0,incoming_sdn_socket,outgoing_socket)


class ErrorManagerNoErrorTest(WriteThroughManagerBase):

    def __init__(self):
        super(ErrorManagerNoErrorTest,self).__init__(generate_no_error)
        
    def test_name(self):
        return 'ErrorManagerNoError'
    
