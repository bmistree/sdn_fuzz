import struct
from ryu.ofproto.ofproto_v1_0_parser import (
    _register_parser, _set_msg_type, OFPFlowMod, OFPMatch, OFPAction)
from ryu.ofproto.ofproto_v1_0 import (
    OFP_MATCH_PACK_STR, OFP_MATCH_SIZE, OFP_HEADER_SIZE,
    OFP_FLOW_MOD_PACK_STR0,OFPT_FLOW_MOD, OFP_FLOW_MOD_SIZE)


@_register_parser
@_set_msg_type(OFPT_FLOW_MOD)
class FlowModParser(object):
    
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        offset = OFP_HEADER_SIZE
        # read match, which is an offset of OFP_HEADER_SIZE away
        match = OFPMatch.parse(buf, offset)
        
        # read additional flow mod info
        offset += OFP_MATCH_SIZE

        (cookie, command,idle_timeout,hard_timeout,priority,
         buffer_id,out_port,flags) = struct.unpack_from(
            OFP_FLOW_MOD_PACK_STR0,buf, offset)

        offset = OFP_FLOW_MOD_SIZE
        
        # read actions
        actions = []
        while offset < msg_len:
            action = OFPAction.parser(buf, offset)
            actions.append(action)
            offset += action.len

        # generate message from all deconstructed fields
        flowmod_msg = OFPFlowMod(
            datapath,match,cookie,command,idle_timeout,
            hard_timeout,priority, buffer_id, out_port,
            flags, actions)

        flowmod_msg.set_headers(version,msg_type,msg_len,xid)
        return flowmod_msg


############ HANDLE PARSING BARRIERS ######################
    
from ryu.ofproto.ofproto_v1_0_parser import OFPBarrierRequest
from ryu.ofproto.ofproto_v1_0 import OFPT_BARRIER_REQUEST

@_register_parser
@_set_msg_type(OFPT_BARRIER_REQUEST)
class BarrierRequestParser(object):
    
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        to_return = OFPBarrierRequest(datapath)
        to_return.set_headers(version,msg_type,msg_len,xid)
        return to_return

############ HANDLE PARSING ALL OTHER TYPES ######################


class UnparsedMessage(object):
    '''
    Controller to switch messages do not all have deserializers
    defined for them.  Of these, we only really need to be able to
    distinguish barrier requests and flow mods, which we do above.
    All other messages can just get passed back and forth, without
    being deserialized.  As a result, this class just wraps the
    underlying raw bytes of such a message.
    '''
    def __init__(self,datapath,version,msg_type,msg_len,xid,buf):
        self.datapath = datapath
        self.version = version
        self.msg_type = msg_type
        self.msg_len = msg_len
        self.xid = xid
        self.buf = buf

    def serialize(self):
        '''
        Do nothing in this method.  Only adding it so that have
        symmetry with other ryu messages.
        '''
        

from ryu.ofproto.ofproto_v1_0 import OFPT_FEATURES_REQUEST
@_register_parser
@_set_msg_type(OFPT_FEATURES_REQUEST)
class DummyFeaturesRequestParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)

    
from ryu.ofproto.ofproto_v1_0 import OFPT_GET_CONFIG_REQUEST
@_register_parser
@_set_msg_type(OFPT_GET_CONFIG_REQUEST)
class DummyGetConfigRequestParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)

    
from ryu.ofproto.ofproto_v1_0 import OFPT_SET_CONFIG
@_register_parser
@_set_msg_type(OFPT_SET_CONFIG)
class DummySetConfigParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)

    
from ryu.ofproto.ofproto_v1_0 import OFPT_PACKET_OUT
@_register_parser
@_set_msg_type(OFPT_PACKET_OUT)
class DummyPacketOutParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)

    
from ryu.ofproto.ofproto_v1_0 import OFPT_PORT_MOD
@_register_parser
@_set_msg_type(OFPT_PORT_MOD)
class DummyPortModParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)


from ryu.ofproto.ofproto_v1_0 import OFPT_QUEUE_GET_CONFIG_REQUEST
@_register_parser
@_set_msg_type(OFPT_QUEUE_GET_CONFIG_REQUEST)
class DummyQueueGetConfigRequestParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)

    
from ryu.ofproto.ofproto_v1_0 import OFPT_STATS_REQUEST
@_register_parser
@_set_msg_type(OFPT_STATS_REQUEST)
class DummyQueueGetConfigRequestParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)

    
from ryu.ofproto.ofproto_v1_0 import OFPT_FEATURES_REPLY
from ryu.ofproto.ofproto_v1_0_parser import _MSG_PARSERS
del _MSG_PARSERS[OFPT_FEATURES_REPLY]
@_register_parser
@_set_msg_type(OFPT_FEATURES_REPLY)
class DummyFeaturesReplyParser(object):
    @classmethod
    def parser(cls, datapath, version, msg_type, msg_len, xid, buf):
        return UnparsedMessage(datapath,version,msg_type,msg_len,xid,buf)
