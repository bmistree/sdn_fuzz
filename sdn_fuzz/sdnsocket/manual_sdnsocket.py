from sdnsocket import SDNSocket
from threading import RLock, Condition


class ManualSDNSocket(SDNSocket):

    def __init__(self):
        # append end, remove front.
        self._received_bytes_array = bytearray()
        self._receive_lock = RLock()
        self._array_condition = Condition(self._receive_lock)

        self._written_bytes_array = bytearray()
        self._write_lock = RLock()
        self._written_array_condition = Condition(self._write_lock)

        
    def read(self,num_bytes_to_read):
        '''
        Threadsafe.
        
        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        return self._internal_read(
            self._received_bytes_array,self._receive_lock,num_bytes_to_read)

    
    def blocking_read(self,num_bytes_to_read):
        '''
        Threadsafe.  Doesn't return until can return some bytes.

        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        return self._internal_blocking_read(
            self._received_bytes_array,self._receive_lock,
            self._array_condition, num_bytes_to_read)

    
    def write_into_read(self,bytes_to_write):
        '''
        Threadsafe.
        
        @param {bytearray} bytes_to_write
        '''
        self._internal_write(
            self._received_bytes_array,self._receive_lock,
            self._array_condition,bytes_to_write)

        
    def write(self,bytes_to_write):
        '''
        Threadsafe.  Write into other endpoint's buffer.

        @param {bytearray} bytes_to_write
        '''
        self._internal_write(
            self._written_bytes_array,self._write_lock,
            self._written_array_condition,bytes_to_write)

        
    def _internal_write(self,array_to_use,lock_to_use,condition_to_use,
                       bytes_to_write):
        with lock_to_use:
            array_to_use.extend(bytes_to_write)
            condition_to_use.notify()

            
    def _internal_read(self,array_to_use,lock_to_use,num_bytes_to_read):
        to_return = bytearray()
        with lock_to_use:
            to_return = array_to_use[0:num_bytes_to_read]
            del array_to_use[0:num_bytes_to_read]
        return to_return

    
    def _internal_blocking_read(self,array_to_use,lock_to_use,
                                condition_to_use,num_bytes_to_read):
        to_return = bytearray()
        condition_to_use.acquire()
        while True:
            to_return = self._internal_read(
                array_to_use,lock_to_use,num_bytes_to_read)
            if len(to_return) != 0:
                break
            condition_to_use.wait()

        condition_to_use.release()
        return to_return

            
    def read_written(self,num_bytes_to_read):
        return self._intenral_read(
            self._written_bytes_array,self._write_lock,num_bytes_to_read)


    def blocking_read_written(self,num_bytes_to_read):
        '''
        Threadsafe.  Doesn't return until can return some bytes.

        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        return self._internal_blocking_read(
            self._written_bytes_array,self._write_lock,
            self._written_array_condition, num_bytes_to_read)
