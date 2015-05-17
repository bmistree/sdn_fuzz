import socket
import threading
import time
import datetime
from ..sdn_message_reader import SDNMessageReader
from ryu.ofproto.ofproto_v1_0 import OFPT_BARRIER_REQUEST, OFPT_FLOW_MOD

class TimedReverseFlowmodsMessageManager(object):
    '''
    When receive flow mod sdn messages on incoming queue, delay until:

      1) Receive a barrier or
      2) A user-specified period of time has expired since received
         last flow mod.
      
    If either of these happen, send out buffered flow mods in reverse
    order of when they were accepted.
    '''
    
    def __init__(self,timeout_seconds,receiver_socket,sender_socket):
        '''
        @param {float} timeout_seconds --- If we have not received a
        flow mod in this many seconds, then send all buffered flow
        mods in reverse order.
        
        @param {SDNSocket} receiver_socket --- Reads messages on this
        socket and instantly forwards them on sender_socket.

        @param {SDNSocket} sender_socket --- Forwards openflow
        messages out of this socket.
        '''
        self.timeout_seconds = timeout_seconds
        
        self.sdn_message_reader = SDNMessageReader(receiver_socket)
        self.sender_socket = sender_socket
        # Elements are byte arrays/strings for openflow messages since
        # last barrier message.
        self.received_flowmods_list = []
        self.last_received_time = None
        self._received_flow_mods_lock = threading.RLock()
        

    def check_time_expired_thread(self):
        '''
        Runs, periodically checking whether it's been
        self.timeout_seconds since the last flow mod has been
        received, and send buffered flow mods if it has been.
        '''
        sleep_time = .5
        while True:
            time.sleep(sleep_time)
            with self._received_flow_mods_lock:
                # empty flowmods list.
                if self.last_received_time is None:
                    sleep_time = .5
                    continue

                # check when the last sent flowmod was received.
                current_time = datetime.datetime.now()
                diff = current_time - self.last_received_time
                seconds_since_last_flowmod = diff.total_seconds()
                if seconds_since_last_flowmod >= self.timeout_seconds:
                    self._send_outstanding()
                    sleep_time = .5
                else:
                    sleep_time =  (
                        self.timeout_seconds - seconds_since_last_flowmod + .01)
        
        
    def start_service(self):
        '''
        Actually start listening for openflow messages and forwarding
        them.
        '''
        t = threading.Thread(target=self._start_forwarding)
        t.setDaemon(True)
        t.start()
        t_watchdog = threading.Thread(target=self.check_time_expired_thread)
        t_watchdog.setDaemon(True)
        t_watchdog.start()


    def _send_outstanding(self,barrier_message_buf=None):
        '''
        @param {bytearray} barrier_message_buf --- None if we aren't
        supposed to send a barrier message.  
        '''
        with self._received_flow_mods_lock:
            # by default, we forward flowmods in reverse order.
            for msg_buf_to_write in reversed(self.received_flowmods_list):
                self.sender_socket.write(msg_buf_to_write)

            self.received_flowmods_list = []
                
            if barrier_message_buf is not None:
                self.sender_socket.write(barrier_message_buf)

            # reset receipt timer because sent out last outstanding
            # message.
            self.last_received_time = None

            
    def _start_forwarding(self):
        while True:
            # msg will either be a ryu message or an unparsed message.
            # in either case, should support serialize + buf calls.
            msg = self.sdn_message_reader.blocking_read_sdn_message()
            msg.serialize()

            with self._received_flow_mods_lock:
                try:
                    if msg.msg_type == OFPT_BARRIER_REQUEST:
                        self._send_outstanding(msg.original_buffer)
                    elif msg.msg_type == OFPT_FLOW_MOD:
                        self.last_received_time = datetime.datetime.now()
                        self.received_flowmods_list.append(msg.original_buffer)
                    else:
                        # just forward the message along: it's non-barrier
                        # and non-flow mod
                        self.sender_socket.write(msg.original_buffer)
                except socket.error:
                    break
