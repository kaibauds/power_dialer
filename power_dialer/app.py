import pprint
import sys
from queue import Queue
from threading import Thread

from pampy import _, match

import power_dialer.models.agent_state as agent_state
import power_dialer.ports.leads_pool as leads_pool
import power_dialer.ports.dialer as dialer
import power_dialer.utils as utils
from power_dialer.power_dialer import PowerDialer

""" The app is a singleton, let's make it explorable"""
the_app = None


def start():
    sys.modules[__name__].PowerDialerApp()
    leads_pool.init()


def shutdown():
    global the_app
    try:
        del the_app
    except Exception:
        pass


def add_power_dialer(agent_id):
    """
    Call this function to attach an agent to the Power Dialer subsystem
    """
    try:
        the_app.add_power_dialer(agent_id)
    except Exception:
        pass


def delete_power_dialer(agent_id):
    """
    Call this function to detach an agent off the Power Dialer subsystem
    """
    try:
        the_app.delete_power_dialer(agent_id)
    except Exception:
        pass


def log_in_agent(agent_id):
    global the_app
    try:
        the_app.agent_power_dialer_map[agent_id].agent_log_in()
    except Exception:
        print(Exception)
        pass


def log_out_agent(agent_id):
    global the_app
    try:
        the_app.agent_power_dialer_map[agent_id].agent_log_out()
    except Exception:
        pass


def print_agent_status(agent_id):
    global the_app
    try:
        power_dialer = the_app.agent_power_dialer_map[agent_id]
        pprint.pp(vars(power_dialer))
        utils.print_a_line()
        pprint.pp(vars(power_dialer.state))
    except Exception:
        pass


def list_all_agents():
    return list(agent for agent in the_app.agent_power_dialer_map)


def list_all_power_dialers():
    return the_app.agent_power_dialer_map


def print_all_test_leads():
    all_test_leads= dialer.all_test_leads()
    for x in all_test_leads:
        print(x, all_test_leads[x])


def add_test_lead(number, arg):
    dialer.add_test_lead(number, arg)


class PowerDialerApp(utils.Singleton):
    agent_power_dialer_map = dict()
    event_queue = Queue()

    def __init__(self):
        global the_app
        the_app = self
        if not agent_state.exists():
            agent_state.create_table()

        for s in agent_state.get_all():
            """
            In the very begining, there's no agent attached to the Power Dialer subsystem.
            An agent must be attached to Power Dialer through either the module or the
            class function 'add_power_dialer'.
            The system may restart and use the persisted state.
            """
            self.add_power_dialer(s.agent_id)
        Thread(target=self.event_loop, daemon=True).start()

    def add_power_dialer(self, agent_id):
        self.event_queue.put(("add_power_dialer", agent_id))

    def delete_power_dialer(self, agent_id):
        self.event_queue.put(("delete_power_dialer", agent_id))

    def event_loop(self):
        match(
            self.event_queue.get(),
            ("add_power_dialer", _),
            self.on_add_power_dialer,
            ("delete_power_dialer", _),
            self.on_delete_power_dialer,
        )
        self.event_loop()

    def on_add_power_dialer(self, agent_id):
        agent_state.init(agent_id)
        if agent_id not in self.agent_power_dialer_map:
            self.agent_power_dialer_map[agent_id] = PowerDialer(agent_id)

    def on_delete_power_dialer(self, agent_id):
        try:
            agent_state.delete(agent_id)
            self.agent_power_dialer_map[agent_id].terminate()
            del self.agent_power_dialer_map[agent_id]
        except Exception:
            pass
