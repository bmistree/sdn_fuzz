#!/usr/bin/env python

# adding sdn_fuzz to sys.path
import os
import sys
base_dir = os.path.dirname(os.path.abspath(__file__))

sdn_fuzz_folder = os.path.join(base_dir,'..')
sys.path.append(sdn_fuzz_folder)

# adding ryu to system path
sys.path.append(os.path.join(base_dir,'..','submodules','ryu'))

# adding ryu extend to system path and forcing it to be used as
import ryu_extend.additional_parsers


import socket
import time

from interpose_arg_helper import parse_args, ReorderType

from sdn_fuzz.sdnsocket.tcp_sdnsocket import TCPSDNSocket
from sdn_fuzz.message_manager.write_through_message_manager import (
    WriteThroughMessageManager)
from sdn_fuzz.message_manager.reverse_flowmods_message_manager import (
    ReverseFlowmodsMessageManager)

'''
Allows running an interposition layer between controller and switch.

See interpose_arg_helper.parse_args for expected input arguments.
'''

    
def run(reorder_type, listen_on_addr, controller_addr,additional_args):
    '''
    @param {ReorderType.X} reorder_type
    
    @param {interpose_arg_helper.HostPortArgument} listen_on_addr ---
    Should listen on this address for connections from a switch.
    
    @param {interpose_arg_helper.HostPortArgument} controller_addr ---
    Should connect to this address as soon as we have a connection
    from a switch.

    @param {str or None} additional_args --- Additional args required
    to initialize the selected reorder type.
    '''

    # start by listening for socket connections from switch
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((listen_on_addr.hostname, listen_on_addr.port))
    s.listen(1)

    switch_socket, _ = s.accept()
    sdn_switch_socket = TCPSDNSocket(switch_socket)

    # switch has connected, connect to controller
    controller_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    controller_socket.connect((controller_addr.hostname, controller_addr.port))
    sdn_controller_socket = TCPSDNSocket(controller_socket)

    # set managers for socket connections in each direction.  for
    # controller-to-switch traffic, decide on manager based on
    # argument.
    controller_to_switch_manager = None
    if reorder_type == ReorderType.WRITE_THROUGH:
        controller_to_switch_manager = WriteThroughMessageManager(
            sdn_controller_socket,sdn_switch_socket)
    elif reorder_type == ReorderType.REVERSE:
        controller_to_switch_manager = ReverseFlowmodsMessageManager(
            sdn_controller_socket,sdn_switch_socket)
    #### DEBUG
    else:
        assert False,'Unexpected reorder type'
    #### END DEBUG

    # switch to controller manager: do not do any reordering
    switch_to_controller_manager = WriteThroughMessageManager(
        sdn_switch_socket, sdn_controller_socket)
        
    # start both managers
    switch_to_controller_manager.start_service()
    controller_to_switch_manager.start_service()
    
    while True:
        time.sleep(5)


if __name__ == '__main__':
    (reorder_type,listen_on_addr,controller_addr,additional_args) = (
        parse_args())
    run(reorder_type,listen_on_addr,controller_addr,additional_args)
