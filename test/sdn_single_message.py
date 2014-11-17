import os
import sys
import time
from threading import Thread

sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),'..','submodules','ryu'))
from ryu.ofproto import nx_match
from ryu.ofproto import ofproto_v1_0_parser
from ryu.ofproto import ofproto_v1_0
from ryu.ofproto.ofproto_protocol import ProtocolDesc
import ryu.ofproto.ofproto_v1_0 as ofproto_v1_0


sdn_fuzz_folder = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),'..')
sys.path.append(sdn_fuzz_folder)

from test_class import TestClass
from sdn_fuzz.sdnsocket.manual_sdnsocket import ManualSDNSocket
from sdn_fuzz.sdn_message_reader import SDNMessageReader

OF_1_0_DATAPATH = ProtocolDesc(ofproto_v1_0.OFP_VERSION)


class SDNSingleMessageTest(TestClass):

    def test_name(self):
        return 'SDNSingleMessage'
    
    def run_test(self):
        '''
        @returns {boolean} --- True if test passed, false otherwise.
        '''
        sdn_socket = ManualSDNSocket()
        sdn_message_reader = SDNMessageReader(sdn_socket)

        # write a flowmod
        written_sdn_message = self._generate_add_flowmod()
        written_sdn_message.serialize()
        sdn_socket.write(written_sdn_message.buf)
        
        # read sdn message from system.
        read_sdn_message = sdn_message_reader.blocking_read_sdn_message()

        # check that read sdn message is same as sent.
        if written_sdn_message != read_sdn_message:
            return False

        return True
        

    def _generate_add_flowmod(self):
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
