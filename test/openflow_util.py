import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),'..','submodules','ryu'))


from ryu.ofproto import nx_match
from ryu.ofproto import ofproto_v1_0_parser
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto.ofproto_protocol import ProtocolDesc
import ryu.ofproto.ofproto_v1_0 as ofproto_v1_0

OF_1_0_DATAPATH = ProtocolDesc(ofproto_v1_0.OFP_VERSION)


def generate_add_flowmod(in_port=None):
    if in_port is None:
        in_port = 32
    rule = nx_match.ClsRule()
    rule.set_in_port(in_port)
    match_tuple = rule.match_tuple()
    match = ofproto_v1_0_parser.OFPMatch(*match_tuple)

    cookie = 0
    command = ofproto_v1_0.OFPFC_ADD
    idle_timeout = 0
    hard_timeout = 0
    priority = ofproto_v1_0.OFP_DEFAULT_PRIORITY
    buffer_id=0xffffffff
    out_port = ofproto_v1_0.OFPP_NONE
    flags = 0
    actions=None
    datapath = OF_1_0_DATAPATH

    return ofproto_v1_0_parser.OFPFlowMod(
        datapath, match, cookie, command, idle_timeout, hard_timeout,
        priority, buffer_id, out_port, flags, actions)

def generate_barrier():
    return ofproto_v1_0_parser.OFPBarrierRequest(OF_1_0_DATAPATH)

def generate_config_request():
    return ofproto_v1_0_parser.OFPGetConfigRequest(OF_1_0_DATAPATH)

