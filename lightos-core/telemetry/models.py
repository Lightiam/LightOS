"""
Telemetry DB — SQLite-backed model-job event store.
Schema designed for Model-Job Template learning (Antigravity Epic 4).
"""
import sqlite3
import time
import uuid
import json
from typing import List, Dict, Any


DDL = """
CREATE TABLE IF NOT EXISTS telemetry_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id      TEXT NOT NULL,
    model_tier  TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    prompt_tokens INTEGER DEFAULT 0,
    completion_tokens INTEGER DEFAULT 0,
    latency_ms  REAL DEFAULT 0,
    cache_hit   INTEGER DEFAULT 0,
    cache_type  TEXT,
    topology_domain TEXT,
    user_id     TEXT,
    app_id      TEXT,
    matched_rule TEXT,
    cost_usd    REAL DEFAULT 0,
    context_chunks_used INTEGER DEFAULT 0,
    created_at  REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_created_at ON telemetry_events(created_at);
CREATE INDEX IF NOT EXISTS idx_model_tier ON telemetry_events(model_tier);
CREATE INDEX IF NOT EXISTS idx_topology ON telemetry_events(topology_domain);
"""


class TelemetryDB:
    def __init__(self, db_path: str):
        self.path = db_path
        self._init()

    def _conn(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._conn() as conn:
            conn.executescript(DDL)

    def insert(self, event: Dict[str, Any]):
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO telemetry_events
                  (job_id, model_tier, tokens_used, prompt_tokens, completion_tokens,
                   latency_ms, cache_hit, cache_type, topology_domain, user_id, app_id,
                   matched_rule, cost_usd, context_chunks_used, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                event.get("job_id", str(uuid.uuid4())[:12]),
                event.get("model_tier", "lightbase"),
                event.get("tokens_used", 0),
                event.get("prompt_tokens", 0),
                event.get("completion_tokens", 0),
                event.get("latency_ms", 0),
                1 if event.get("cache_hit") else 0,
                event.get("cache_type"),
                event.get("topology_domain", "dc-1-rack-a"),
                event.get("user_id", "anonymous"),
                event.get("app_id", "default"),
                event.get("matched_rule", "default"),
                event.get("cost_usd", 0),
                event.get("context_chunks_used", 0),
                time.time()
            ))

    def count(self) -> int:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) as c FROM telemetry_events").fetchone()
            return row["c"]

    def recent_jobs(self, limit: int = 50) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT job_id, model_tier, tokens_used, latency_ms,
                       cache_hit, cache_type, topology_domain, user_id, app_id,
                       matched_rule, cost_usd, context_chunks_used,
                       datetime(created_at, 'unixepoch') as created_at
                FROM telemetry_events
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(r) for r in rows]

    def summary(self) -> Dict[str, Any]:
        with self._conn() as conn:
            totals = conn.execute("""
                SELECT
                    COUNT(*) as total_jobs,
                    SUM(tokens_used) as total_tokens,
                    SUM(cost_usd) as total_cost_usd,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(cache_hit) * 100 as cache_hit_rate_pct,
                    COUNT(DISTINCT user_id) as unique_users
                FROM telemetry_events
            """).fetchone()

            by_tier = conn.execute("""
                SELECT model_tier,
                       COUNT(*) as jobs,
                       SUM(tokens_used) as tokens,
                       SUM(cost_usd) as cost_usd,
                       AVG(latency_ms) as avg_latency_ms,
                       AVG(cache_hit) * 100 as cache_hit_pct
                FROM telemetry_events
                GROUP BY model_tier
            """).fetchall()

            by_domain = conn.execute("""
                SELECT topology_domain,
                       COUNT(*) as jobs,
                       AVG(latency_ms) as avg_latency_ms,
                       SUM(tokens_used) as tokens
                FROM telemetry_events
                GROUP BY topology_domain
            """).fetchall()

            return {
                "totals": dict(totals) if totals else {},
                "by_tier": [dict(r) for r in by_tier],
                "by_topology_domain": [dict(r) for r in by_domain],
                "timestamp": time.time()
            }

    def model_job_templates(self) -> List[Dict]:
        """Cluster jobs into Model-Job Templates by (model_tier, topology_domain)."""
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT model_tier, topology_domain,
                       COUNT(*) as job_count,
                       AVG(tokens_used) as avg_tokens,
                       AVG(latency_ms) as avg_latency_ms,
                       AVG(cost_usd) as avg_cost_usd,
                       AVG(cache_hit) * 100 as cache_hit_pct,
                       AVG(context_chunks_used) as avg_chunks
                FROM telemetry_events
                GROUP BY model_tier, topology_domain
                ORDER BY job_count DESC
            """).fetchall()
            return [dict(r) for r in rows]

    def hourly_series(self, hours: int = 24) -> List[Dict]:
        """Return hourly aggregated metrics for time-series chart."""
        since = time.time() - (hours * 3600)
        with self._conn() as conn:
            rows = conn.execute("""
                SELECT
                    strftime('%Y-%m-%d %H:00', datetime(created_at, 'unixepoch')) as hour,
                    COUNT(*) as jobs,
                    SUM(tokens_used) as tokens,
                    SUM(cost_usd) as cost_usd,
                    AVG(latency_ms) as avg_latency_ms,
                    AVG(cache_hit) * 100 as cache_hit_pct
                FROM telemetry_events
                WHERE created_at >= ?
                GROUP BY hour
                ORDER BY hour ASC
            """, (since,)).fetchall()
            return [dict(r) for r in rows]
