import threading
from ..sdn_message_reader import SDNMessageReader
from ryu.ofproto.ofproto_v1_0 import OFPT_BARRIER_REQUEST, OFPT_FLOW_MOD

class ReverseFlowmodsMessageManager(object):
    '''
    When receive sdn messages on incoming queue, instantly write it
    out on sender socket.
    '''

    def __init__(self,receiver_socket,sender_socket):
        '''
        @param {SDNSocket} receiver_socket --- Reads messages on this
        socket and instantly forwards them on sender_socket.

        @param {SDNSocket} sender_socket --- Forwards openflow
        messages out of this socket.
        '''
        self.sdn_message_reader = SDNMessageReader(receiver_socket)
        self.sender_socket = sender_socket
        # Elements are byte arrays/strings for openflow messages since
        # last barrier message.
        self.received_flowmods_list = []

    def start_service(self):
        '''
        Actually start listening for openflow messages and forwarding
        them.
        '''
        t = threading.Thread(target=self._start_forwarding)
        t.setDaemon(True)
        t.start()


    def _send_outstanding(self,pre_barrier_message_list,barrier_message_buf):
        '''
        @param {list} pre_barrier_message_list --- Each element is a
        byte array or a string corresponding to an openflow message
        received before barrier message.

        @param {bytearray} barrier_messgae_buf --- A buffer sending
        the barrier along.
        '''
        # by default, we forward flowmods in reverse order.
        for msg_buf_to_write in reversed(pre_barrier_message_list):
            self.sender_socket.write(msg_buf_to_write)
        self.sender_socket.write(barrier_message_buf)

        
    def _start_forwarding(self):
        while True:
            # msg will either be a ryu message or an unparsed message.
            # in either case, should support serialize + buf calls.
            msg = self.sdn_message_reader.blocking_read_sdn_message()
            msg.serialize()

            if msg.msg_type == OFPT_BARRIER_REQUEST:
                self._send_outstanding(
                    self.received_flowmods_list,msg.original_buffer)
            elif msg.msg_type == OFPT_FLOW_MOD:
                self.received_flowmods_list.append(msg.original_buffer)
            else:
                # just forward the message along
                self.sender_socket.write(msg.original_buffer)
