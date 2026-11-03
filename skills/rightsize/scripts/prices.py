"""List prices for Claude models, USD per million tokens.

Source: platform.claude.com pricing and prompt-caching pages, checked 2026-10-27.
Re-check before quoting dollars: prices change. Cache writes cost 1.25x input
(5-minute TTL) or 2x input (1-hour TTL); cache reads use a per-model rate.
"""

from dataclasses import dataclass
from typing import Any, Optional, cast


@dataclass(frozen=True)
class Price:
    input: float
    output: float
    cache_read: float
    # Haiku 5.5 bills a higher rate once a single prompt exceeds 100k tokens.
    long_threshold: Optional[int] = None
    long_input: Optional[float] = None
    long_output: Optional[float] = None


PRICES = {
    "claude-fable-5-1": Price(10.0, 50.0, 0.25),
    "claude-fable-5": Price(10.0, 50.0, 1.0),
    "claude-opus-5-5": Price(4.0, 20.0, 0.20),
    "claude-opus-5": Price(5.0, 25.0, 0.50),
    "claude-opus-4-8": Price(5.0, 25.0, 0.50),
    "claude-opus-4-7": Price(5.0, 25.0, 0.50),
    "claude-opus-4-6": Price(5.0, 25.0, 0.50),
    "claude-sonnet-5-5": Price(2.0, 10.0, 0.20),
    "claude-sonnet-5": Price(2.0, 10.0, 0.20),
    "claude-sonnet-4-6": Price(3.0, 15.0, 0.30),
    "claude-haiku-5-5": Price(0.10, 0.50, 0.01, 100_000, 0.50, 2.50),
    "claude-haiku-4-5": Price(1.0, 5.0, 0.10),
}

ALIASES = {
    "fable": "claude-fable-5-1",
    "opus": "claude-opus-5-5",
    "sonnet": "claude-sonnet-5-5",
    "haiku": "claude-haiku-5-5",
}

CACHE_WRITE_5M = 1.25
CACHE_WRITE_1H = 2.0


def resolve(model: str) -> Optional[str]:
    """Map an alias or a dated/suffixed model id to a key of PRICES."""
    if not model:
        return None
    name = ALIASES.get(model, model).split("[")[0]
    if name in PRICES:
        return name
    # Longest prefix wins so "claude-opus-5-5-x" maps to opus-5-5, not opus-5.
    matches = [key for key in PRICES if name.startswith(key)]
    return max(matches, key=len) if matches else None


def request_cost(model: str, usage: dict[str, Any]) -> Optional[float]:
    """Dollar cost of one API response from its `usage` block, or None if unpriced."""
    key = resolve(model)
    if key is None:
        return None
    price = PRICES[key]
    fresh = usage.get("input_tokens", 0) or 0
    read = usage.get("cache_read_input_tokens", 0) or 0
    written = usage.get("cache_creation_input_tokens", 0) or 0
    split = usage.get("cache_creation") or {}
    written_1h = split.get("ephemeral_1h_input_tokens", 0) or 0
    written_5m = split.get("ephemeral_5m_input_tokens", written - written_1h) or 0
    output = usage.get("output_tokens", 0) or 0

    rate_in, rate_out = price.input, price.output
    if price.long_threshold and fresh + read + written > price.long_threshold:
        rate_in = cast(float, price.long_input)
        rate_out = cast(float, price.long_output)

    dollars = (
        fresh * rate_in
        + written_5m * rate_in * CACHE_WRITE_5M
        + written_1h * rate_in * CACHE_WRITE_1H
        + read * price.cache_read * (rate_in / price.input)
        + output * rate_out
    )
    return dollars / 1_000_000
