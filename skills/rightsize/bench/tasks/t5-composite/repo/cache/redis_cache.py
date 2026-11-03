RETRY_MULTIPLIER = 3.0
BACKOFF_FACTOR = 1.2


def backoff(attempt):
    return 0.05 * (BACKOFF_FACTOR ** attempt) * RETRY_MULTIPLIER
