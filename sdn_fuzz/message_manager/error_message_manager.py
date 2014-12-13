import threading
from ..sdn_message_reader import SDNMessageReader
from ryu.ofproto.ofproto_v1_0 import OFPT_BARRIER_REQUEST, OFPT_FLOW_MOD

# handling failure messages
from ryu.ofproto.ofproto_v1_0 import OFPET_FLOW_MOD_FAILED, OFPFMFC_UNSUPPORTED
from ryu.ofproto.ofproto_v1_0_parser import OFPErrorMsg


def generate_error_from_flow_mod(flow_mod_message):
    '''
    Should already be compiled
    '''
    fail_type = OFPET_FLOW_MOD_FAILED
    fail_code = OFPFMFC_UNSUPPORTED
    data = flow_mod_message.buf[0:60]
    to_return = OFPErrorMsg(flow_mod_failed, fail_code,data)
    to_return.xid = flow_mod_message.xid
    return to_return


class ErrorFlowmodsMessageManager(object):
    '''
    When receive sdn messages on incoming queue, instantly write it
    out on sender socket.
    '''
    
    def __init__(self,receiver_socket,sender_socket):
        '''
        @param {SDNSocket} receiver_socket --- Reads messages on this
        socket and instantly forwards them on sender_socket.  Note: if
        we decied to send an error for this flow mod, then we send the
        error out on this socket.

        @param {SDNSocket} sender_socket --- Forwards openflow
        messages out of this socket that do not have errors.
        '''
        self.receiver_socket = receiver_socket
        self.sdn_message_reader = SDNMessageReader(receiver_socket)
        self.sender_socket = sender_socket


    def start_service(self):
        '''
        Actually start listening for openflow messages and forwarding
        them.
        '''
        t = threading.Thread(target=self._start_forwarding)
        t.setDaemon(True)
        t.start()

    def check_fail_flow_mod(self,incoming_flow_mod_msg):
        '''
        @param {FlowModMessage} incoming_flow_mod_msg
        
        @returns {None or error message} --- If None, just forward
        message along.  If error message, then an error message
        generated for the target flow mod.

        Children should subclass this method to handle define a new
        fail_flow_mod.  Currently, does not fail any messages.
        '''
        return None

    
    def _start_forwarding(self):
        while True:
            # msg will either be a ryu message or an unparsed message.
            # in either case, should support serialize + buf calls.
            msg = self.sdn_message_reader.blocking_read_sdn_message()
            msg.serialize()
            
            if msg.msg_type == OFPT_FLOW_MOD:
                failure_msg = self.check_fail_flow_mod(msg.buf)
                if failure_msg is None:
                    # just forward the message along
                    self.sender_socket.write(msg.buf)
                else:
                    # we should send the failure message back to the
                    # socket we received the message on.
                    self.receiver_socet.write(failure_msg.buf)
            else:
                # just forward the message along
                self.sender_socket.write(msg.buf)

