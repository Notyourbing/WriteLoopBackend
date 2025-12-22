import time
import threading
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger("RateLimiter")

class TokenBucket:
    """
    Thread-safe implementation of the Token Bucket algorithm for API rate limiting.
    Used to control traffic spikes and ensure system stability.
    """
    
    def __init__(self, capacity: int, refill_rate: float):
        """
        :param capacity: Maximum number of tokens in the bucket
        :param refill_rate: Tokens added per second
        """
        self._capacity = float(capacity)
        self._tokens = float(capacity)
        self._refill_rate = refill_rate
        self._last_refill = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: int = 1) -> bool:
        """
        Attempt to consume tokens. Returns True if successful, False otherwise.
        """
        with self._lock:
            self._refill()
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

    def _refill(self):
        now = time.time()
        delta = now - self._last_refill
        tokens_to_add = delta * self._refill_rate
        self._tokens = min(self._capacity, self._tokens + tokens_to_add)
        self._last_refill = now

class APIRateLimiter:
    """
    Manager class to handle rate limits for different IP addresses or User IDs.
    """
    
    def __init__(self):
        self._buckets: Dict[str, TokenBucket] = {}
        self._default_limit = (60, 1.0) # 60 reqs burst, 1 req/sec refill
        self._vip_limit = (200, 5.0)    # 200 reqs burst, 5 req/sec refill
        self._lock = threading.Lock()

    def get_bucket(self, key: str, is_vip: bool = False) -> TokenBucket:
        with self._lock:
            if key not in self._buckets:
                capacity, rate = self._vip_limit if is_vip else self._default_limit
                self._buckets[key] = TokenBucket(capacity, rate)
            return self._buckets[key]

    def allow_request(self, client_id: str, is_vip: bool = False) -> bool:
        """
        Check if the request is allowed for the given client_id.
        """
        bucket = self.get_bucket(client_id, is_vip)
        allowed = bucket.consume(1)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for client: {client_id}")
        
        return allowed

    def cleanup_stale_buckets(self, ttl: int = 3600):
        """
        Remove buckets that haven't been accessed in TTL seconds to free memory.
        """
        with self._lock:
            current_time = time.time()
            keys_to_remove = []
            for key, bucket in self._buckets.items():
                if current_time - bucket._last_refill > ttl:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._buckets[key]
            
            if keys_to_remove:
                logger.info(f"Cleaned up {len(keys_to_remove)} stale rate limit buckets")

# Global instance
limiter = APIRateLimiter()