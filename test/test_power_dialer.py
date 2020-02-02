from power_dialer import power_dialer


def test_fib() -> None:
    assert power_dialer.fib(0) == 0
    assert power_dialer.fib(1) == 1
    assert power_dialer.fib(2) == 1
    assert power_dialer.fib(3) == 2
    assert power_dialer.fib(4) == 3
    assert power_dialer.fib(5) == 5
    assert power_dialer.fib(10) == 55
