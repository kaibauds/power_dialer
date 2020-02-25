from threading import Lock

plock = Lock()


def print_a_line(n=40):
    print("".join(list("_" for i in range(n))))


def thprint(*a, **b):
    global plock
    with plock:
        print(*a, **b)


class Singleton:
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Singleton, cls).__new__(cls)

        return cls.instance
