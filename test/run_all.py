#!/usr/bin/env python

from manual_socket import ManualSocketTest
from sdn_single_message import SDNSingleMessageTest
from write_through_manager import WriteThroughManagerTest
from reverse_manager import ReverseManagerTest
from error_manager_no_error import ErrorManagerNoErrorTest
from error_manager_all_errors import ErrorManagerAllErrorsTest
from tcp_write_through import TCPWriteThroughTest
from timed_reverse_manager import TimedReverseManagerTest

test_class_constructors = [
    SDNSingleMessageTest,
    WriteThroughManagerTest,
    ReverseManagerTest,
    ManualSocketTest,
    ErrorManagerNoErrorTest,
    ErrorManagerAllErrorsTest,
    TCPWriteThroughTest,
    TimedReverseManagerTest
    ]

def run_all():
    for test_class_constructor in test_class_constructors:
        test_class = test_class_constructor()
        print '\n'
        print 'Test: ' + test_class.test_name()
        print '    ',
        if test_class.run_test():
            print 'SUCCEEDED'
        else:
            print 'FAILED'
        print '\n'


if __name__ == '__main__':
    run_all()
