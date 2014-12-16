import threading

class TCPSDNSocket(object):

    def __init__(self,socket):
        '''
        @param {BSD socket} socket --- Should already have been
        connected or accepted.
        '''
        self.socket = socket
        self.read_lock = threading.RLock()
        self.write_lock = threading.RLock()
    
    def read(self,num_bytes_to_read):
        '''
        Threadsafe.
        
        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        assert(False,'Only allow blocking reads on tcp.')

    def blocking_read(self,num_bytes_to_read):
        '''
        Threadsafe.  Doesn't return until can return some bytes.

        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        with self.read_lock:
            return bytearray(self.socket.recv(num_bytes_to_read))

    def write_into_read(self,bytes_to_write):
        '''
        Threadsafe.  Write into read buffer.
        
        @param {bytearray} bytes_to_write
        '''
        assert(False,'Disallowing write_into_read for tcp sockets')

    def write(self, bytes_to_write):
        '''
        Threadsafe.  Write into other endpoint's buffer.

        @param {bytearray} bytes_to_write
        '''
        with self.write_lock:
            self.socket.sendall(bytes_to_write)
