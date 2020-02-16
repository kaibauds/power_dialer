import test.simulators.ext_dialer as ext_dialer
from queue import Queue
from threading import Thread

# Alternatively, the simulator module can be loaded
# dynamically when it is not PROD environment.
# from importlib import import_module


def _port_func_dial(env):
    if env != "PROD":

        """
        Dialer simulator is used for non-prodction environment
        """
        return ext_dialer.dial

    else:
        """
        The actual external port fucntion for dialing
        in the production environment should be referred here
        """
        return lambda arg: None


def _port_func_watch_call(env):
    if env != "PROD":

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


"""
Every dialing will be a Dialer object, so that functions
such as "end_dialing" can be provided with the object
"""


class Dialer:
    number = None
    port_func_dial = None
    result = Queue()
    call = None

    def __init__(self, number, env="PROD", arg=None):
        self.number = number
        self.port_func_dial = _port_func_dial(env)

        """
        dial() should be called sychronously in a thread, so that
        the Dialer instance can be returned immediately
        """

        Thread.run(self._dial, [self, number, env, arg])

    def _dial(self, number, env, arg):

        dialing_result = self.port_func_dial(number, arg)

        if dialing_result == "SUCCESS":

            """
            A Call() object is a part of return so that the client will have
            the handle to access functions such as end_the_call() when necessary.
            """
            self.result.put(("SUCCESS", Call(self.number, env, arg)))
        else:
            self.result.put("FAIL")

    def get_result(self):
        return self.result.get()

    def end_dialing():
        """ end a dialing gracefully here """
        pass


class Call:
    result = Queue()
    number = None

    def __init__(self, number, env="PROD", arg=None):
        self.number = number
        self.port_func_watch_call = _port_func_watch_call(env)
        Thread.run(self._watch_the_call, [self, number, env, arg])

    def _watch_the_call(self, number, env, arg):
        self.port_func_watch_call(number, arg)
        self.result.put("CALL_END")

    def get_result(self):
        return self.result.get()

    def end_the_call(self):
        """ end a call gracefully here """
        pass
