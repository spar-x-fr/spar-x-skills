"""A weighted LRU cache with per-entry time-to-live.

- `capacity` is the maximum total weight the cache may hold.
- `put(key, value, weight=1, ttl=None)` stores or replaces an entry. `ttl` is in
  seconds; None means the entry never expires. An entry whose weight alone exceeds
  the capacity is not stored (and any previous value for that key is removed).
- `get(key, default=None)` returns the value if present and not expired, and marks
  the entry as most recently used.
- An entry put at time t with ttl T is alive while now < t + T, and expired from
  t + T on.
- When the total weight exceeds the capacity, least recently used entries are
  evicted until it fits. Expired entries are removed before any eviction.
- `len(cache)` counts live (non-expired) entries only; `cache.weight` is the total
  weight of live entries.
"""

import time
from collections import OrderedDict


class TTLCache:
    def __init__(self, capacity, clock=time.monotonic):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._clock = clock
        self._data = OrderedDict()  # key -> (value, weight, expires_at)
        self._weight = 0

    def _expired(self, expires_at):
        return expires_at is not None and self._clock() > expires_at

    def _purge(self):
        for key in list(self._data):
            if self._expired(self._data[key][2]):
                self._weight -= self._data[key][1]
                del self._data[key]

    def put(self, key, value, weight=1, ttl=None):
        if weight > self.capacity:
            return
        expires_at = None if ttl is None else self._clock() + ttl
        self._data[key] = (value, weight, expires_at)
        self._weight += weight
        self._purge()
        while self._weight > self.capacity:
            old_key, (_, old_weight, _) = self._data.popitem(last=True)
            self._weight -= old_weight

    def get(self, key, default=None):
        entry = self._data.get(key)
        if entry is None or self._expired(entry[2]):
            return default
        return entry[0]

    def __len__(self):
        return len(self._data)

    @property
    def weight(self):
        return self._weight
