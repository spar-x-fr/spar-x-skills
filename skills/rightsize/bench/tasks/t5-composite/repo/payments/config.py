from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    payment_max_attempts: int = 4
    backoff_base: float = 0.25
    backoff_multiplier: float = 2.0  # legacy, unused since v3


settings = Settings()
