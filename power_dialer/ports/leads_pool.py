from queue import Queue

"""
Leads pool for the app is a singleton, 
so leads_pool can be an accessible global variable.
"""

leads_pool = None


class LeadsPool(Queue):
    def __init__(self):
        global leads_pool
        leads_pool = self


def get_lead_phone_number_to_dial():
    global leads_pool
    try:
        return leads_pool.get_nowait()
    except any:
        return None


def put_phone_number_into_leads_pool(number):
    global leads_pool
    leads_pool.put(number)


def init_leads_pool():
    global leads_pool
    leads_pool = LeadsPool()
