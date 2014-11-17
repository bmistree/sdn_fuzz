from sdnsocket import SDNSocket
from threading import RLock, Condition


class ManualSDNSocket(SDNSocket):

    def __init__(self):
        # append end, remove front.
        self._received_bytes_array = bytearray()
        self._receive_lock = RLock()
        self._array_condition = Condition(self._receive_lock)
        
        
    def read(self,num_bytes_to_read):
        '''
        Threadsafe.
        
        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        with self._receive_lock:
            to_return = self._received_bytes_array[0:num_bytes_to_read]
            del self._received_bytes_array[0:num_bytes_to_read]
            return to_return

    def blocking_read(self,num_bytes_to_read):
        '''
        Threadsafe.  Doesn't return until can return some bytes.

        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        to_return = bytearray()
        self._array_condition.acquire()
        while True:
            to_return = self.read(num_bytes_to_read)
            if len(to_return) == 0:
                break
            self._array_condition.await()
            
        self._array_condition.release()
        return to_return
        
    def write(self,bytes_to_write):
        '''
        Threadsafe.
        
        @param {bytearray} bytes_to_write
        '''
        with self._receive_lock:
            self._received_bytes_array.extend(bytes_to_write)
            self._array_condition.notify()
