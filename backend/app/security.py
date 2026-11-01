import hashlib
import hmac
import time
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from .models import RateBucket

def rate_allowed(sessions, secret: str, scope: str, address: str, limit: int, window: int = 3600) -> bool:
    """Atomic fixed-window limiter shared by API processes. Never stores raw IPs."""
    now = time.time()
    bucket = int(now // window)
    digest = hmac.new(secret.encode(), f"{scope}:{address}:{bucket}".encode(), hashlib.sha256).hexdigest()
    with sessions.begin() as db:
        insert = pg_insert if db.bind.dialect.name == "postgresql" else sqlite_insert
        stmt = insert(RateBucket).values(key=digest, count=1, expires_at=(bucket + 1) * window)
        stmt = stmt.on_conflict_do_update(index_elements=[RateBucket.key],
            set_={"count": RateBucket.count + 1}).returning(RateBucket.count)
        count = db.scalar(stmt)
        db.execute(delete(RateBucket).where(RateBucket.expires_at < now - window))
        return count <= limit
