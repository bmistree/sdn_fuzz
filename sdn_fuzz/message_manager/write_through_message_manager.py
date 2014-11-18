import threading

from ..sdn_message_reader import SDNMessageReader


class WriteThroughMessageManager(object):
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


    def start_service(self):
        '''
        Actually start listening for openflow messages and forwarding
        them.
        '''
        t = threading.Thread(target=self._start_forwarding)
        t.setDaemon(True)
        t.start()


    def _start_forwarding(self):
        while True:
            # msg will either be a ryu message or an unparsed message.
            # in either case, should support serialize + buf calls.
            msg = self.sdn_message_reader.blocking_read_sdn_message()
            msg.serialize()
            self.sender_socket.write(msg.buf)
