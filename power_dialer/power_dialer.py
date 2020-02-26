# from power_dialer.app import PowerDialerApp
from datetime import datetime, timedelta
from queue import Queue
from threading import Thread
from warnings import warn

from pampy import _, match

import power_dialer.models.agent_state as agent_state

# from power_dialer.ports.dialer import Call
import power_dialer.ports.leads_pool as leads_pool
import power_dialer.utils as utils
from power_dialer.ports.dialer import Dialer

"""
The maximum parallel dialings for an agent.
"""
DIAL_RATIO = 2

"""
There shouldn't be endless call existing, it is necessary to check the
last_action_time of the latest state change to decide if the agent is INACTIVE.
When the 'INACTIVE' is identified the first time, the sytem should request
the agent's action; consecutively the 2nd time the system should end
the call if there's live call instatnce and log out the agent.
"""
KEEP_ALIVE_INTERVAL = 3600


class PowerDialer:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.state = agent_state.query(agent_id)
        self.event_queue = Queue()
        self.lead_dialer_map = dict()
        self.call = None
        self.dialing_in_parallel = 0
        Thread(target=self.event_loop, daemon=True).start()

    def event_loop(self):
        if (
            match(
                self.event_queue.get(),
                "login",
                self.on_agent_login,
                "dialing",
                self.on_dialing,
                ("call_fail", _),
                self.on_call_failed,
                ("call_drop", _),
                self.on_call_dropped,
                ("call_start", _),
                self.on_call_started,
                ("call_end", _),
                self.on_call_ended,
                "logout",
                self.on_agent_logout,
                "stop",
                lambda _e: "stop",
            )
            != "stop"
        ):
            self.event_loop()

    def update_state(self, attr_dict):
        self.state = agent_state.update(self.state, attr_dict)

    def agent_log_in(self):
        self.event_queue.put("login")

    def agent_log_out(self):
        self.event_queue.put("logout")

    def trigger_dialing(self):
        self.event_queue.put("dialing")

    def notify_dialing_fail(self, number):
        self.event_queue.put(("call_fail", number))

    def notify_drop_dialing(self, number):
        self.event_queue.put(("call_drop", number))

    def notify_call_started(self, call):
        self.event_queue.put(("call_start", call))

    def notify_call_end(self, number):
        self.event_queue.put(("call_end", number))

    def terminate(self):
        self.event_queue.put("stop")

    def dial_sync(self):
        lead_number = leads_pool.take_a_lead()
        utils.thprint(
            f"{utils.time_now()}---- dialing         ---- number {lead_number} ---- agent {self.agent_id} ----"
        )
        dialer = Dialer(lead_number)
        """
        There is no race condition concern with the following
        due to the lead number being the index.
        """
        self.lead_dialer_map[lead_number] = dialer
        dialing_result = dialer.get_result()
        match(
            dialing_result,
            ("SUCCESS", _),
            self.notify_call_started,
            ("FAIL", _),
            self.notify_dialing_fail,
            ("DROP", _),
            self.notify_drop_dialing,
        )

    def call_sync(self):
        match(
            self.call.get_result(),
            ("CALL_END", _),
            self.notify_call_end,
            _,
            lambda _e: None,
        )

    def multi_dial_parallel(self, n):
        for i in range(n):
            Thread(target=self.dial_sync, daemon=True).start()

    def on_agent_login(self, _e):
        utils.thprint(f"---- Agent {self.agent_id} logged in ----")
        if self.state.status in {"OFF", "INACTIVE"}:
            self.update_state({"status": "READY", "last_action_time": datetime.now()})
            self.trigger_dialing()

    def on_dialing(self, _e):
        # utils.thprint(f"---- Dialing is launched for agent {self.agent_id}  ----")
        global DIAL_RATIO
        if self.state.status in ("OFF", "IN_CALL"):
            warn("wrong state")
            return
        if self.state.status == "READY":
            self.multi_dial_parallel(DIAL_RATIO - self.dialing_in_parallel)
            self.dialing_in_parallel = DIAL_RATIO

    def on_call_failed(self, number):
        self.dialing_in_parallel -= 1
        utils.thprint(
            f"{utils.time_now()}---- dialing fail    ---- number {number} ---- agent {self.agent_id} ----"
        )
        if number in self.lead_dialer_map.keys():
            del self.lead_dialer_map[number]
        if self.state.status == "READY":
            self.trigger_dialing()

    def on_call_dropped(self, number):
        self.dialing_in_parallel -= 1
        utils.thprint(
            f"{utils.time_now()}---- dialing dropped ---- number {number} ---- agent {self.agent_id} ----"
        )
        if number in self.lead_dialer_map.keys():
            del self.lead_dialer_map[number]
        if self.state.status == "READY":
            self.trigger_dialing()

    def on_call_started(self, call):
        self.dialing_in_parallel -= 1
        utils.thprint(
            f"{utils.time_now()}---- call started    ---- number {call.number} ---- agent {self.agent_id} ----"
        )
        if self.state.status == "READY":
            self.call = call
            self.update_state(
                {
                    "status": "IN_CALL",
                    "latest_lead": call.number,
                    "timestatmp": datetime.now(),
                }
            )
            for dialer in self.lead_dialer_map.values():
                if dialer.number != call.number:
                    dialer.end_dialing()
                    """ put the losing lead back to the leads pool"""
                    leads_pool.add_a_lead(dialer.number)
                # gracefully end the dialing to the losing leads
                del dialer
            self.lead_dialer_map.clear()
            Thread(target=self.call_sync, daemon=True).start()
        else:
            """Force the termination of the call if the state is not right"""
            utils.thprint(
                f"{utils.time_now()}---- terminate call ---- number {call.number} ---- agent {self.agent_id} ----"
            )
            self.call.end_the_call()

    def on_call_ended(self, number):
        utils.thprint(
            f"{utils.time_now()}---- call ended     ---- number {number} ---- agent {self.agent_id} ----"
        )
        if self.state.status == "IN_CALL":
            self.call = None
            self.update_state({"status": "READY", "last_action_time": datetime.now()})
            self.trigger_dialing()

    def on_agent_logout(self, _e):
        utils.thprint(f"---- agent {self.agent_id} logged out ----")
        if self.state.status != "OFF":
            self.update_state({"status": "OFF", "last_action_time": datetime.now()})

    def on_keep_alive(self, _e):
        if self.state.status == "INACTIVE":
            self.update_state({"status": "OFF"})
        elif (
            self.state.status == "IN_CALL"
            and timedelta.total_seconds(datetime.now() - self.state.last_action_time)
            > KEEP_ALIVE_INTERVAL
        ):
            self.update_state({"status": "INACTIVE"})
