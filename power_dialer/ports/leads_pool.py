from queue import Queue

from power_dialer.utils import Singleton

leads_pool = None


class LeadsPool(Singleton, Queue):
    def __init__(self):
        global leads_pool
        leads_pool = self
        super(LeadsPool, self).__init__()


def take_a_lead():
    global leads_pool
    try:
        return leads_pool.get()
    except Exception:
        return None


def add_a_lead(number):
    global leads_pool
    leads_pool.put(number)


def add_leads(numbers):
    global leads_pool
    for number in numbers:
        add_a_lead(number)


def init():
    global leads_pool
    leads_pool = LeadsPool()
