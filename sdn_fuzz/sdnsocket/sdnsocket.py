
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

    def write(self,bytes_to_write):
        '''
        Threadsafe.
        
        @param {bytearray} bytes_to_write
        '''
        pass
