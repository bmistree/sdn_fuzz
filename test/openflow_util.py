import os
import sys

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),'..','submodules','ryu'))

from ryu.lib import addrconv
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

def generate_switch_features_buffer():
    '''
    Almost directly copied from ryu's
    test_parser_v10.TestOFPPortStatus
    '''
    version = {'buf': '\x01', 'val': ofproto_v1_0.OFP_VERSION}
    msg_type = {'buf': '\x06', 'val': ofproto_v1_0.OFPT_FEATURES_REPLY}
    msg_len_val = ofproto_v1_0.OFP_SWITCH_FEATURES_SIZE \
        + ofproto_v1_0.OFP_PHY_PORT_SIZE
    msg_len = {'buf': '\x00\x50', 'val': msg_len_val}
    xid = {'buf': '\xcc\x0a\x41\xd4', 'val': 3423224276}

    # OFP_SWITCH_FEATURES_PACK_STR
    # '!QIB3xII'...datapath_id, n_buffers, n_tables,
    #              zfill, capabilities, actions
    datapath_id = {'buf': '\x11\xa3\x72\x63\x61\xde\x39\x81',
                   'val': 1270985291017894273}
    n_buffers = {'buf': '\x80\x14\xd7\xf6', 'val': 2148849654}
    n_tables = {'buf': '\xe4', 'val': 228}
    zfill = '\x00' * 3
    capabilities = {'buf': '\x69\x4f\xe4\xc2', 'val': 1766843586}
    actions = {'buf': '\x78\x06\xd9\x0c', 'val': 2013714700}

    # OFP_PHY_PORT_PACK_STR
    # '!H6s16sIIIIII'... port_no, hw_addr, name, config, state
    #                    curr, advertised, supported, peer
    port_no = {'buf': '\xe7\x6b', 'val': 59243}
    hw_addr = '3c:d1:2b:8d:3f:d6'
    name = 'name'.ljust(16)
    config = {'buf': '\x84\xb6\x8c\x53', 'val': 2226555987}
    state = {'buf': '\x64\x07\xfb\xc9', 'val': 1678244809}
    curr = {'buf': '\xa9\xe8\x0a\x2b', 'val': 2850556459}
    advertised = {'buf': '\x78\xb9\x7b\x72', 'val': 2025421682}
    supported = {'buf': '\x7e\x65\x68\xad', 'val': 2120575149}
    peer = {'buf': '\xa4\x5b\x8b\xed', 'val': 2757463021}

    buf = version['buf'] \
        + msg_type['buf'] \
        + msg_len['buf'] \
        + xid['buf'] \
        + datapath_id['buf'] \
        + n_buffers['buf'] \
        + n_tables['buf'] \
        + zfill \
        + capabilities['buf'] \
        + actions['buf'] \
        + port_no['buf'] \
        + addrconv.mac.text_to_bin(hw_addr) \
        + name \
        + config['buf'] \
        + state['buf'] \
        + curr['buf'] \
        + advertised['buf'] \
        + supported['buf'] \
        + peer['buf']

    return buf
