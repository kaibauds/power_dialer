from queue import Queue

from power_dialer.utils import Singleton

leads_pool = None


class LeadsPool(Singleton, Queue):
    def __init__(self):
        global leads_pool
        leads_pool = self
        super(LeadsPool, self).__init__()


def get():
    global leads_pool
    try:
        return leads_pool.get()
    except Exception:
        return None


def put(number):
    global leads_pool
    leads_pool.put(number)


def init():
    global leads_pool
    leads_pool = LeadsPool()
