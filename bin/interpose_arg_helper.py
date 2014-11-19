import argparse
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

    
def parse_args():
    '''
    @returns 3-tuple: type, listen_on_addr, controller_addr
    '''
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

    return args.type, args.listen_on_addr, args.controller_addr
    
