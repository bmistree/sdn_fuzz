
from sdnsocket import SDNSocket
from threading import RLock


class ManualSDNSocket(SDNSocket):

    def __init__(self):
        # append end, remove front.
        self._received_bytes_array = bytearray()
        self._array_lock = RLock()
        
    def read(self,num_bytes_to_read):
        '''
        Threadsafe.
        
        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        with self._receive_lock:
            to_return = self._received_bytes_array[0:num_bytes_to_read]
            del self._received_bytes_array[0:num_bytes_to_read]
            return to_return

    def write(self,bytes_to_write):
        '''
        Threadsafe.
        
        @param {bytearray} bytes_to_write
        '''
        with self._receive_lock:
            self._received_bytes_array.extend(bytes_to_write)

        
