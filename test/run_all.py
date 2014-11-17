#!/usr/bin/env python

from manual_socket import ManualSocketTest

test_class_constructors = [
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
