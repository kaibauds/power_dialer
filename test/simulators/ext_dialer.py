from time import sleep


"""
The simulator of the dialer. The time taken for the dialing and
calling will be passed in as testing arguments.
For example,
    test_arg=('SUCCESS', 0.1, 0.2)
Means dialing will succeed in 100 millisecond and the call will alst 200 millisecond.
"""


def dial(number, test_arg):
    (dialing_result, delay, _call_length) = test_arg
    sleep(delay)
    return dialing_result


def watch_call(number, test_arg):
    (_dialing_result, _delay, call_length) = test_arg
    sleep(call_length)
    return "CALL_END"
