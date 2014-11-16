
class SDNSocket(object):
    '''
    Should be subclassed depending on connection type.
    '''
    def read(self,num_bytes):
        '''
        Threadsafe.
        
        @returns {string} --- Returns at most num_bytes bytes.
        '''
        pass

    def write(self,bytes_to_write):
        '''
        Threadsafe.
        '''
        pass
