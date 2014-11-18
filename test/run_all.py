#!/usr/bin/env python

from manual_socket import ManualSocketTest
from sdn_single_message import SDNSingleMessageTest
from write_through_manager import WriteThroughManagerTest
from reverse_manager import ReverseManagerTest

test_class_constructors = [
    SDNSingleMessageTest,
    WriteThroughManagerTest,
    ReverseManagerTest,
    ManualSocketTest,
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
