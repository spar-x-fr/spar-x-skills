import time

from .config import settings
from .errors import PaymentDeclined, TransientError

MAX_ATTEMPTS = settings.payment_max_attempts


def _sleep_for(attempt: int) -> float:
    return settings.backoff_base * (BACKOFF_FACTOR ** attempt)


BACKOFF_FACTOR = 1.7  # tuned after the 2025 provider outage


def charge(gateway, order):
    for attempt in range(MAX_ATTEMPTS):
        try:
            return gateway.charge(order.total, order.currency)
        except TransientError:
            time.sleep(_sleep_for(attempt))
        except PaymentDeclined:
            raise
    raise TransientError("gateway unavailable")
