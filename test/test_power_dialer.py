from power_dialer.app import PowerDialerApp
from power_dialer.ports.leads_pool import LeadsPool

test_leads_result_dict = {
    1: ("SUCESS", 0, 0.1),
    2: ("SUCESS", 0.1, 0.1),
    3: ("SUCESS", 0.15, 0.1),
    4: ("FAIL", 0, None),
    5: ("FAIL", 0.1, None),
    6: ("FAIL", 0.15, None),
}


def test_login_quicker_lead_win():
    app = PowerDialerApp()
    app.add_agent_dialer("Alice")
    leads_pool = LeadsPool()
    leads_pool.put(2)
    leads_pool.put(1)
    sleep
