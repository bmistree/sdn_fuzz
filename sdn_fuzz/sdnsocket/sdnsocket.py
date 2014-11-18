
class SDNSocket(object):
    '''
    Should be subclassed depending on connection type.
    '''
    def read(self,num_bytes_to_read):
        '''
        Threadsafe.
        
        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        pass

    def blocking_read(self,num_bytes_to_read):
        '''
        Threadsafe.  Doesn't return until can return some bytes.

        @returns {bytearray} --- Returns at most num_bytes bytes.
        '''
        pass

    def write_into_read(self,bytes_to_write):
        '''
        Threadsafe.  Write into read buffer.
        
        @param {bytearray} bytes_to_write
        '''
        pass

    def write(self, bytes_to_write):
        '''
        Threadsafe.  Write into other endpoint's buffer.

        @param {bytearray} bytes_to_write
        '''
