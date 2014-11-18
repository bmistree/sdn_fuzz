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
