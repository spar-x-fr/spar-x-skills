"""Delivery route planning."""


def cheapest_tour(n, roads, depot, stops, max_tolls):
    """Return the minimum total cost of a tour, or -1 if no tour exists.

    n:         number of junctions, numbered 0 .. n-1.
    roads:     list of (a, b, cost, toll) tuples. Roads are two-way; cost is a
               positive integer; toll is True for a toll road.
    depot:     the junction where the tour starts and ends.
    stops:     junctions the tour must visit at least once each (any order; it
               may contain the depot, duplicates, or be empty).
    max_tolls: the tour may traverse toll roads at most this many times in total
               (traversing the same toll road twice counts twice).

    A tour may revisit junctions and roads. An empty `stops` costs 0.
    It must stay fast for n = 200 junctions, 1 000 roads, 8 stops and
    max_tolls = 4 (well under two seconds in CPython).
    """
    raise NotImplementedError
