"""Single-machine job scheduling with precedence constraints."""


def schedule(jobs, before):
    """Return an order of all job names that respects `before` and minimises
    the maximum lateness.

    jobs:   {name: (duration, deadline)}, durations are positive integers.
    before: list of (a, b) pairs meaning job a must finish before job b starts.
    Jobs run back to back from time 0. The lateness of a job is its completion
    time minus its deadline (it can be negative). Must handle a few hundred jobs
    in well under a second. Raise ValueError if the constraints contain a cycle.
    """
    raise NotImplementedError
