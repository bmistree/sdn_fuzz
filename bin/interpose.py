#!/usr/bin/env python

import socket

from interpose_arg_helper import parse_args, ReorderType
        
    
def run(reorder_type, listen_on_addr,controller_addr):
    '''
    @param {ReorderType.X} reorder_type
    
    @param {HostPortArgument} listen_on_addr --- Should listen on this
    address for connections from a switch.
    
    @param {string} controller_addr --- Should connect to this address
    as soon as we have a connection from a switch.
    '''
    print '\nGot into run\n'


if __name__ == '__main__':
    (reorder_type,listen_on_addr,controller_addr) = parse_args()
    run(reorder_type,listen_on_addr,controller_addr)
