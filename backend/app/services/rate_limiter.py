import time
import fnmatch
from typing import Dict, List, Tuple
from collections import deque

class SecurityGovernor:
    """
    Sliding window rate-limiter and Referer/IP whitelist validator.
    """
    def __init__(self):
        # key_str -> deque of request timestamps
        self.request_records: Dict[str, deque] = {}

    def check_rate_limit(self, key: str, qpm: int) -> bool:
        """Returns True if request is ALLOWED, False if RATE LIMITED."""
        if qpm <= 0:
            return True
        now = time.time()
        window_start = now - 60.0
        
        if key not in self.request_records:
            self.request_records[key] = deque()
            
        record = self.request_records[key]
        while record and record[0] < window_start:
            record.popleft()
            
        if len(record) >= qpm:
            return False
            
        record.append(now)
        return True

    def check_referer(self, referer: str, whitelist: List[str]) -> bool:
        """Returns True if Referer is allowed."""
        if not whitelist:
            return True
        if not referer:
            # If whitelist is explicitly set but referer is empty, allow or block based on config
            return False
            
        # Clean domain
        from urllib.parse import urlparse
        parsed = urlparse(referer)
        domain = parsed.netloc.split(":")[0].lower() or referer.lower()
        
        for pattern in whitelist:
            pattern = pattern.strip().lower()
            if fnmatch.fnmatch(domain, pattern):
                return True
        return False

    def check_ip(self, client_ip: str, whitelist: List[str]) -> bool:
        """Returns True if IP is in whitelist."""
        if not whitelist:
            return True
        if not client_ip:
            return True
        for ip in whitelist:
            if client_ip == ip.strip():
                return True
        return False

security_governor = SecurityGovernor()
