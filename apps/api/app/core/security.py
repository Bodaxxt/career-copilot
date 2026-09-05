from datetime import datetime, timedelta
from typing import Optional
import hmac
import hashlib

def generate_mock_token(user_id: str) -> str:
    """Generate mock authentication token."""
    raw = f"{user_id}:{datetime.utcnow().timestamp()}"
    return hashlib.sha256(raw.encode()).hexdigest()
