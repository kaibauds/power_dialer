# Power Dialer Manual Integration Testing
&nbsp;
```
(power_dialer) kai@deb9:~/power_dialer$ python3.8
Python 3.8.1 (default, Feb  1 2020, 18:49:37)
[GCC 6.3.0 20170516] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
>>> import power_dialer.app as app
>>>
>>> import power_dialer.ports.leads_pool as lp
>>>
>>> app.start()
>>>
>>> app.list_all_agents()
['Kai']
>>>
>>> app.delete_power_dialer("Kai")
>>>
>>> app.list_all_agents()
[]
>>>
>>> app.add_power_dialer("Kai")
>>>
>>> app.list_all_agents()
['Kai']
>>>
>>> app.print_agent_status("Kai")
{'agent_id': 'Kai',
 'state': agent_state<Kai>,
 'event_queue': <queue.Queue object at 0x7f9e7af19a60>,
 'lead_dialer_map': {},
 'call': None,
 'dialing_in_parallel': 0}
________________________________________
{'attribute_values': {'status': 'OFF', 'agent_id': 'Kai'}}
>>>
>>> app.log_in_agent("Kai")
>>> ---- Agent Kai logged in ----

>>> app.print_agent_status("Kai")
{'agent_id': 'Kai',
 'state': agent_state<Kai>,
 'event_queue': <queue.Queue object at 0x7f9e7af19a60>,
 'lead_dialer_map': {},
 'call': None,
 'dialing_in_parallel': 2}
________________________________________
{'attribute_values': {'status': 'READY',
                      'agent_id': 'Kai',
                      'last_action_time': datetime.datetime(2020, 2, 26, 13, 35, 3, 745526)}}
>>>
>>> app.print_all_test_leads()
000-0000 ('SUCCESS', 15, 30)
111-1111 ('SUCCESS', 10, 20)
222-2222 ('SUCCESS', 0.2, 0.2)
333-3333 ('FAIL', 5, 0)
444-4444 ('FAIL', 0.2, 0)
555-5555 ('FAIL', 0.3, 0)
>>>
>>> app.add_test_lead('888-8888', ('SUCCESS', 3, 10))
>>>
>>> app.print_all_test_leads()
000-0000 ('SUCCESS', 15, 30)
111-1111 ('SUCCESS', 10, 20)
222-2222 ('SUCCESS', 0.2, 0.2)
333-3333 ('FAIL', 5, 0)
444-4444 ('FAIL', 0.2, 0)
555-5555 ('FAIL', 0.3, 0)
888-8888 ('SUCCESS', 3, 10)
>>>
>>> lp.add_leads(["000-0000", "333-3333", "111-1111", "222-2222", "888-8888"])
13:35:52---- dialing         ---- number 000-0000 ---- agent Kai ----
13:35:52---- dialing         ---- number 333-3333 ---- agent Kai ----
>>> 13:35:57---- dialing fail    ---- number 333-3333 ---- agent Kai ----
13:35:57---- dialing         ---- number 111-1111 ---- agent Kai ----
13:36:07---- call started    ---- number 000-0000 ---- agent Kai ----
13:36:07---- dialing dropped ---- number 111-1111 ---- agent Kai ----
13:36:37---- call ended     ---- number 000-0000 ---- agent Kai ----
13:36:37---- dialing         ---- number 222-2222 ---- agent Kai ----
13:36:37---- dialing         ---- number 888-8888 ---- agent Kai ----
13:36:37---- call started    ---- number 222-2222 ---- agent Kai ----
13:36:37---- dialing dropped ---- number 888-8888 ---- agent Kai ----
13:36:37---- call ended     ---- number 222-2222 ---- agent Kai ----
13:36:37---- dialing         ---- number 111-1111 ---- agent Kai ----
13:36:37---- dialing         ---- number 888-8888 ---- agent Kai ----
13:36:40---- call started    ---- number 888-8888 ---- agent Kai ----
13:36:40---- dialing dropped ---- number 111-1111 ---- agent Kai ----
13:36:50---- call ended     ---- number 888-8888 ---- agent Kai ----
13:36:50---- dialing         ---- number 111-1111 ---- agent Kai ----
13:37:00---- call started    ---- number 111-1111 ---- agent Kai ----
13:37:20---- call ended     ---- number 111-1111 ---- agent Kai ----

>>> app.print_agent_status("Kai")
{'agent_id': 'Kai',
 'state': agent_state<Kai>,
 'event_queue': <queue.Queue object at 0x7f9e7af19a60>,
 'lead_dialer_map': {},
 'call': None,
 'dialing_in_parallel': 2}
________________________________________
{'attribute_values': {'status': 'READY',
                      'agent_id': 'Kai',
                      'last_action_time': datetime.datetime(2020, 2, 26, 13, 37, 20, 556248),
                      'latest_lead': '111-1111'},
 'timestatmp': datetime.datetime(2020, 2, 26, 13, 37, 0, 535853)}
>>>
>>> lp.add_leads(["000-0000", "333-3333", "111-1111", "222-2222", "888-8888"])
13:38:50---- dialing         ---- number 000-0000 ---- agent Kai ----
13:38:50---- dialing         ---- number 333-3333 ---- agent Kai ----
>>> 13:38:55---- dialing fail    ---- number 333-3333 ---- agent Kai ----
13:38:55---- dialing         ---- number 111-1111 ---- agent Kai ----
13:39:05---- call started    ---- number 111-1111 ---- agent Kai ----
13:39:05---- dialing dropped ---- number 000-0000 ---- agent Kai ----
13:39:25---- call ended     ---- number 111-1111 ---- agent Kai ----
13:39:25---- dialing         ---- number 222-2222 ---- agent Kai ----
13:39:25---- dialing         ---- number 888-8888 ---- agent Kai ----
13:39:25---- call started    ---- number 222-2222 ---- agent Kai ----
13:39:25---- dialing dropped ---- number 888-8888 ---- agent Kai ----
13:39:25---- call ended     ---- number 222-2222 ---- agent Kai ----
13:39:25---- dialing         ---- number 000-0000 ---- agent Kai ----
13:39:25---- dialing         ---- number 888-8888 ---- agent Kai ----
13:39:28---- call started    ---- number 888-8888 ---- agent Kai ----
13:39:28---- dialing dropped ---- number 000-0000 ---- agent Kai ----
13:39:38---- call ended     ---- number 888-8888 ---- agent Kai ----
13:39:38---- dialing         ---- number 000-0000 ---- agent Kai ----
13:39:53---- call started    ---- number 000-0000 ---- agent Kai ----
13:40:23---- call ended     ---- number 000-0000 ---- agent Kai ----

>>> app.print_agent_status("Kai")
{'agent_id': 'Kai',
 'state': agent_state<Kai>,
 'event_queue': <queue.Queue object at 0x7f9e7af19a60>,
 'lead_dialer_map': {},
 'call': None,
 'dialing_in_parallel': 2}
________________________________________
{'attribute_values': {'status': 'READY',
                      'agent_id': 'Kai',
                      'last_action_time': datetime.datetime(2020, 2, 26, 13, 40, 23, 900185),
                      'latest_lead': '000-0000'},
 'timestatmp': datetime.datetime(2020, 2, 26, 13, 39, 53, 899399)}
>>>
```