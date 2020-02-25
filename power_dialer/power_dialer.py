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
from power_dialer.utils import thprint

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
        Thread(target=self.event_loop, daemon=True).start()

    def event_loop(self):
        utils.thprint(f"---- agent: {self.agent_id} waiting for event ---")
        if (
            match(
                self.event_queue.get(),
                "login",
                self.on_agent_login,
                "dialing",
                self.on_dialing,
                "call_fail",
                self.on_call_failed,
                ("call_start", _),
                self.on_call_started,
                "call_end",
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

    def notify_dialing_fail(self, _e):
        self.event_queue.put("call_fail")

    def notify_call_started(self, number):
        self.event_queue.put(("call_start", number))

    def notify_call_end(self):
        self.event_queue.put("call_end")

    def terminate(self):
        self.event_queue.put("stop")

    def _handle_success_dialing(self, call):
        setattr(self, "call", call)
        self.notify_call_started(call.number)

    def dial_sync(self):
        lead_number = leads_pool.get()
        dialer = Dialer(lead_number)
        self.lead_dialer_map[lead_number] = dialer
        thprint("<<<<<<<<<<<<<<<")
        match(
            dialer.get_result(),
            ("SUCCESS", _),
            self._handle_success_dialing,
            "FAIL",
            self.notify_dialing_fail,
        )
        thprint(">>>>>>>>>>>>>>")

    def multi_dial_parallel(self, n):
        for i in range(n):
            Thread(target=self.dial_sync, daemon=True).start()

    def on_agent_login(self, _e):
        utils.thprint(f"---- agent {self.agent_id} logged in ----")
        if self.state.status in {"OFF", "INACTIVE"}:
            self.update_state(
                {"status": "READY", "cdc": 0, "last_action_time": datetime.now()}
            )
            self.trigger_dialing()

    def on_dialing(self, _e):
        utils.thprint(f"---- dialing is triggered for agent {self.agent_id}  ----")
        global DIAL_RATIO
        if self.state.status in ("OFF", "IN_CALL"):
            warn("wrong state")
            return
        if self.state.status == "READY":
            cdc = self.state.cdc
            self.update_state({"cdc": DIAL_RATIO})
            self.multi_dial_parallel(DIAL_RATIO - cdc)

    def on_call_failed(self, _e):
        utils.thprint(f"---- A dialing failed for agent {self.agent_id} ----")
        if self.state.status == "READY":
            self.update_state({"cdc": self.state.cdc - 1})
            self.trigger_dialing()

    def on_call_started(self, phone_number):
        utils.thprint(
            f"---- A call to number {phone_number} started for agent {self.agent_id} ----"
        )
        if self.state.status == "READY":
            self.update_state(
                {
                    "status": "IN_CALL",
                    "latest_lead": phone_number,
                    "timestatmp": datetime.now(),
                }
            )
            for dialer in self.lead_dialer_map.values():
                dialer.end_dialing()
        else:
            warn("wrong state")
            self.call.end_call(phone_number)

    def on_call_ended(self, _e):
        utils.thprint(f"---- A call endded for agent {self.agent_id} ----")
        if self.state.status == "IN_CALL":
            self.update_state(
                {"status": "READY", "last_action_time": datetime.now(), "cdc": 0}
            )
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
