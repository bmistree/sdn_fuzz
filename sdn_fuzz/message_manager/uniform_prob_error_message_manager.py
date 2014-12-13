import random
from .error_message_manager import ErrorFlowmodsMessageManager

class UniformProbErrorMessageManager(ErrorFlowmodsMessageManager):

    def __init__(self,failure_probability,receiver_socket,sender_socket):
        '''
        @param {float} failure_probability --- [0,1] chance that
        incoming flow mod gets errored.
        
        For other params, @see ErrorFlowmodsMessageManager.__init___
        '''
        self.failure_probability = failure_probability
        super(UniformProbErrorMessageManager,self).__init__(
            receiver_socket,sender_socket)

    def check_fail_flow_mod(self,incoming_flow_mod_msg):
        '''
        For params @see
        ErrorFlowmodsMessageManager.check_fail_flow_mod
        '''
        
        if random.random() < self.failure_probability:
            # FIXME: actually craft error message here.
            assert False

        # do not fail out.
        return None
