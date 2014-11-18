import threading

from manual_sdnsocket import ManualSDNSocket

def _forward_writes(socket_to_listen_on, socket_to_forward_to):
    '''
    Should be started in separate daemon thread.
    
    @param {ManualSDNSocket} socket_to_listen_on, socket_to_forward_to
    '''
    while True:
        read_buffer = socket_to_listen_on.blocking_read_written(100)
        socket_to_forward_to.write_into_read(read_buffer)
    


def crossover_manual_sdn_socket():
    '''
    @returns (a,b) --- Connected manual sdn sockets.  Creates two
    manual SDN sockets.  Writes on one socket can be read as reads on
    other side.
    '''

    to_return = (ManualSDNSocket(), ManualSDNSocket())

    # start socket 1 listening to socket 0
    t1 = threading.Thread(target=_forward_writes,args=(
            to_return[0],to_return[1]))
    t1.setDaemon(True)
    t1.start()

    # start socket 0 listening to socket 1
    t2 = threading.Thread(target=_forward_writes,args=(
            to_return[1],to_return[0]))
    t2.setDaemon(True)
    t2.start()
        
    return to_return
        
