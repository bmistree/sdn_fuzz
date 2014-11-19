#!/usr/bin/env python

import argparse
import socket
import re

class ReorderType(object):
    WRITE_THROUGH = 'write_through'
    REVERSE = 'reverse'


class HostPortArgument(object):
    def __init__(self,value):
        '''
        @param {string} value --- Should have format
        <hostname>:<port> or
        <ip addr>:<port>
        '''
        regex = '(?P<hostname>[a-zA-Z0-9.]+):(?P<port>\\d+)'

        match = re.match(regex,value)

        if match is None:
            raise argparse.ArgumentTypeError(
                'Required <inet addr>:<port> or <hostname>:<port>')

        self.hostname = match.group('hostname')
        self.port = int(match.group('port'))

    def __str__(self):
        return self.hostname + ':' + str(self.port)
        
    
def run(reorder_type, listen_on_addr,controller_addr):
    '''
    @param {ReorderType.X} reorder_type
    
    @param {HostPortArgument} listen_on_addr --- Should listen on this
    address for connections from a switch.
    
    @param {string} controller_addr --- Should connect to this address
    as soon as we have a connection from a switch.
    '''
    
    
    
def run_cli():
    description_string = 'Use this script to interpose on openflow commands'
    parser = argparse.ArgumentParser(description=description_string)
    
    parser.add_argument(
        '--type',choices=[ReorderType.WRITE_THROUGH,ReorderType.REVERSE],
        default=ReorderType.WRITE_THROUGH,
        help='How to treat flowmods received between barriers')

    parser.add_argument(
        '--listen-on-addr',
        type=HostPortArgument,
        default=HostPortArgument('0.0.0.0:6633'),
        help='We listen for connections from switch on this address.')

    parser.add_argument(
        '--controller-addr',
        type=HostPortArgument,
        help=('When we receive a connection from switch, try to connect' +
              'to a controller at this address.  Format: a.b.c.d:<port>.'),
        required=True)
    
    args = parser.parse_args()

    listen_on_addr = args.listen_on_addr
    controller_addr = args.controller_addr

    print '\n\nGot values'
    print str(listen_on_addr)
    print str(controller_addr)
    print '\n\n'
    
    # if args.type == ReorderType.WRITE_THROUGH:
    #     assert(False,'Still must handle write through reordering.')
    # elif args.type == ReorderType.REVERSE:
    #     assert(False,'Still must handle reverse reordering.')
    # else:
    #     assert(False,'Unexpected reordering type.')
    
    



if __name__ == '__main__':
    run_cli()
    
