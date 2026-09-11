"""
Rate Limiter Guardrail (Phase 7 AI Engine - Architecture v8.0).
Enforces 30 requests/minute per report and 300 requests/hour per user.
"""

import time
from typing import Dict, List, Tuple
from fastapi import HTTPException

class RateLimiter:
    """In-memory sliding window rate limiter."""

    _report_requests: Dict[int, List[float]] = {}
    _user_requests: Dict[int, List[float]] = {}

    MAX_REPORT_RPM = 30
    MAX_USER_RPH = 300

    @classmethod
    def check_rate_limit(cls, report_id: int, user_id: int = 1):
        now = time.time()

        # Report 1-minute window
        timestamps = cls._report_requests.get(report_id, [])
        timestamps = [t for t in timestamps if now - t < 60.0]
        if len(timestamps) >= cls.MAX_REPORT_RPM:
            raise HTTPException(
                status_code=429,
                detail=f"Rate Limit Exceeded: Maximum {cls.MAX_REPORT_RPM} requests per minute per report allowed."
            )
        timestamps.append(now)
        cls._report_requests[report_id] = timestamps

        # User 1-hour window
        u_timestamps = cls._user_requests.get(user_id, [])
        u_timestamps = [t for t in u_timestamps if now - t < 3600.0]
        if len(u_timestamps) >= cls.MAX_USER_RPH:
            raise HTTPException(
                status_code=429,
                detail=f"Rate Limit Exceeded: Maximum {cls.MAX_USER_RPH} requests per hour per user allowed."
            )
        u_timestamps.append(now)
        cls._user_requests[user_id] = u_timestamps
