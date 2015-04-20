from ryu.ofproto.ofproto_common import OFP_HEADER_SIZE
from ryu.ofproto import ofproto_parser
from ryu.ofproto.ofproto_protocol import ProtocolDesc
import ryu.ofproto.ofproto_v1_0 as ofproto_v1_0

_OF_1_0_DATAPATH = ProtocolDesc(ofproto_v1_0.OFP_VERSION)


class SDNMessageReader(object):
    '''
    Used to read full sdn messages from socket.
    '''
    
    def __init__(self,sdn_socket):
        '''
        @param {SDNSocket} sdn_socket
        '''
        self._sdn_socket = sdn_socket
        

    def blocking_read_sdn_message(self,block_read_written=False):
        '''
        @returns an SDN message
        '''
        reader_method = self._sdn_socket.blocking_read
        if block_read_written:
            reader_method = self._sdn_socket.blocking_read_written
        
        # first read openflow header
        msg_buffer = reader_method(OFP_HEADER_SIZE)
        while len(msg_buffer) != OFP_HEADER_SIZE:
            diff = OFP_HEADER_SIZE - len(msg_buffer)
            msg_buffer.extend(reader_method(diff))

        # based on size of openflow header, decide how much more to
        # read
        (version, msg_type, msg_len, xid) = ofproto_parser.header(msg_buffer)

        while len(msg_buffer) != msg_len:
            diff = msg_len - len(msg_buffer)
            msg_buffer.extend(reader_method(diff))
        
        msg = ofproto_parser.msg(
            _OF_1_0_DATAPATH, version, msg_type, msg_len,
            xid, str(msg_buffer))

        msg.original_buffer = msg_buffer
        return msg
