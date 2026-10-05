"""
Centralized In-Memory Sliding-Window Rate Limiter and Brute-Force Abuse Prevention.
Protects sensitive authentication, PIN verification, and mutation endpoints against brute-force and credential stuffing.
"""
import time
import threading
from typing import Dict, List, Tuple, Optional
from app.core.config import settings
from app.core.exceptions import RateLimitExceededError


class SlidingWindowRateLimiter:
    """Thread-safe sliding window in-memory rate limiter."""
    def __init__(self):
        self._lock = threading.Lock()
        self._records: Dict[str, List[float]] = {}

    def is_allowed(self, key: str, limit: int, window_seconds: int = 60) -> Tuple[bool, int, int]:
        """
        Check if an operation under 'key' is permitted within the given rate limit.
        Returns: (is_allowed, current_count, retry_after_seconds)
        """
        if not settings.RATE_LIMIT_ENABLED:
            return True, 0, 0

        now = time.time()
        window_start = now - window_seconds

        with self._lock:
            timestamps = self._records.get(key, [])
            # Evict timestamps outside the sliding window
            valid_timestamps = [t for t in timestamps if t > window_start]

            if len(valid_timestamps) >= limit:
                oldest_in_window = valid_timestamps[0]
                retry_after = max(1, int(oldest_in_window + window_seconds - now))
                self._records[key] = valid_timestamps
                return False, len(valid_timestamps), retry_after

            valid_timestamps.append(now)
            self._records[key] = valid_timestamps
            return True, len(valid_timestamps), 0

    def check(self, key: str, limit: int, window_seconds: int = 60, message: Optional[str] = None) -> None:
        """
        Enforce rate limit. If limit is exceeded, raises RateLimitExceededError.
        """
        allowed, count, retry_after = self.is_allowed(key, limit, window_seconds)
        if not allowed:
            raise RateLimitExceededError(
                retry_after_seconds=retry_after,
                message=message or f"Rate limit exceeded for action. Please retry in {retry_after} second(s)."
            )

    def reset(self, key: str) -> None:
        """Reset rate limit history for a key (e.g. upon successful authentication)."""
        with self._lock:
            self._records.pop(key, None)

    def cleanup(self) -> None:
        """Periodic garbage collection of expired keys."""
        now = time.time()
        with self._lock:
            keys_to_delete = []
            for key, timestamps in self._records.items():
                active = [t for t in timestamps if t > now - 3600]
                if not active:
                    keys_to_delete.append(key)
                else:
                    self._records[key] = active
            for k in keys_to_delete:
                del self._records[k]


rate_limiter = SlidingWindowRateLimiter()
