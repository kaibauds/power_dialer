import app
import leads_pool

test_leads_result_dict = {
    1 : ('hooked', 0, 0.1),
    2 : ('hooked', 0.1, 0.1),
    3 : ('hooked', 0.15, 0.1),
    4 : ('rejected', 0, None),
    5 : ('rejected', 0.1, None),
    6 : ('rejected', 0.15, None)
}


def test_login_quicker_lead_win() :
    app.PowerDialerApp()
    app.PowerDialerApp.add_agent_dialer('Alice')
    leads_pool = LeadsPool()
    leads_pool.put(1) 
    leads_pool.put(2)
    



    assert power_dialer.fib(0) == 0
    assert power_dialer.fib(1) == 1
    assert power_dialer.fib(2) == 1
    assert power_dialer.fib(3) == 2
    assert power_dialer.fib(4) == 3
    assert power_dialer.fib(5) == 
    assert power_dialer.fib(10) == 55
