import test.simulators.ext_dialer as ext_dialer

# import power_dialer.utils as utils
from queue import Queue
from threading import Thread

# from power_dialer.utils import thprint

"""
Spare some numbers exclusivley for testing purpose. Dialer will
use simulators to run the dialing and call for these numbers.
Testing numbers and testing arguments re given in a dictionay.
Testing argument example:
            test_arg=('SUCCESS', 0.1, 0.2)
It means dialing will succeed in 100 millisecond and the call
will alst 200 millisecond.
"""

testing_number_and_arg_dict = {
    "000-0000": ("SUCCESS", 15, 30),
    "111-1111": ("SUCCESS", 10, 20),
    "222-2222": ("SUCCESS", 0.2, 0.2),
    "333-3333": ("FAIL", 5, 0),
    "444-4444": ("FAIL", 0.2, 0),
    "555-5555": ("FAIL", 0.3, 0),
}

default_arg = ("SUCCESS", 0, 3600)


def all_test_leads():
    global testing_number_and_arg_dict
    return testing_number_and_arg_dict


def add_test_lead(lead_number, arg):
    global testing_number_and_arg_dict
    if type(lead_number) == str:
        (result, delay, lasting) = arg
        if (
            result in ["SUCCESS", "FAIL"]
            and type(delay) in [int, float]
            and type(lasting) in [int, float]
        ):
            testing_number_and_arg_dict[lead_number] = arg


def _port_func_dial(phone_number, env):
    global testing_number_and_arg_dict
    if env != "PROD" or phone_number in all_test_leads().keys():

        """
        Dialer simulator is used for non-prodction environment
        """
        return ext_dialer.dial

    else:
        """
        The actual external port fucntion for dialing
        in the production environment should be referred here
        """
        return lambda *arg: None


def _port_func_watch_call(phone_number, env):
    if env != "PROD" or phone_number in testing_number_and_arg_dict.keys():

        """
        Dialer simulator is loaded for non-prodction environment
        """
        return ext_dialer.watch_call

    else:
        """
        The actual external port fucntion for dialing
        in the production environment should be referred here
        """
        return lambda arg: None


class Dialer:
    """
    Each dialing will be a Dialer object
    """

    def __init__(self, number, env="PROD"):
        global testing_number_and_arg_dict, default_arg
        self.number = number
        self.port_func_dial = _port_func_dial(number, env)
        self.result = Queue()
        self.call = None

        """
        dial() should be called sychronously in a thread, so that
        the Dialer object can be returned immediately
        """

        Thread(
            target=self._dial,
            args=(number, env, testing_number_and_arg_dict.get(number, default_arg)),
            daemon=True,
        ).start()

    def _dial(self, number, env, arg):

        dialing_result = self.port_func_dial(number, arg)

        if dialing_result == "SUCCESS":

            """
            A Call() object is a part of return so that the client will have
            the handle to access functions such as end_the_call() when necessary.
            """
            self.result.put(("SUCCESS", Call(self.number, env, arg)))
        else:
            self.result.put(("FAIL", number))

    def get_result(self):
        return self.result.get()

    def end_dialing(self):
        self.result.put(("DROP", self.number))
        """ end a dialing gracefully here """
        pass


class Call:
    def __init__(self, number, env="PROD", arg=None):
        self.number = number
        self.port_func_watch_call = _port_func_watch_call(number, env)
        self.result = Queue()
        Thread(
            target=self._watch_the_call, args=(number, env, arg), daemon=True
        ).start()

    def _watch_the_call(self, number, env, arg):
        self.port_func_watch_call(number, arg)
        self.result.put(("CALL_END", number))

    def get_result(self):
        return self.result.get()

    def end_the_call(self):
        """ end a call gracefully here """
        pass
