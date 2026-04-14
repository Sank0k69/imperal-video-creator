"""
Task Queue — SQLite-backed async task queue.

Zero infrastructure. Works for Video Creator, Daria, Agent Platform.
Upgrade path: swap SQLite → Redis/Celery when scaling to multi-server.

Usage:
    from taskqueue import TaskQueue, TaskStatus

    q = TaskQueue("tasks.db")

    # Register handlers
    @q.handler("generate_video")
    async def handle_video(task_id, payload):
        # long-running work...
        return {"video_url": "..."}

    # Enqueue
    task_id = await q.enqueue("generate_video", {
        "script": "...", "title": "...", "montage": {...}
    })

    # Check status
    status = await q.get(task_id)

    # Start worker (processes queue)
    await q.run_worker(concurrency=3)
"""

import asyncio
import json
import sqlite3
import time
import traceback
import uuid
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Coroutine


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    id: str
    type: str
    status: TaskStatus
    payload: dict
    result: dict | None
    error: str | None
    progress: int  # 0-100
    title: str
    created_at: float
    started_at: float | None
    completed_at: float | None
    retries: int
    max_retries: int


class TaskQueue:
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = Path(db_path)
        self._handlers: dict[str, Callable] = {}
        self._progress_callbacks: dict[str, Callable] = {}
        self._running = False
        self._init_db()

    def _init_db(self):
        """Create tasks table if not exists."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                payload TEXT NOT NULL DEFAULT '{}',
                result TEXT,
                error TEXT,
                progress INTEGER NOT NULL DEFAULT 0,
                title TEXT NOT NULL DEFAULT '',
                created_at REAL NOT NULL,
                started_at REAL,
                completed_at REAL,
                retries INTEGER NOT NULL DEFAULT 0,
                max_retries INTEGER NOT NULL DEFAULT 2
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC)
        """)
        conn.commit()
        conn.close()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def handler(self, task_type: str):
        """Decorator to register a task handler."""
        def decorator(fn):
            self._handlers[task_type] = fn
            return fn
        return decorator

    # ------------------------------------------------------------------
    # Enqueue
    # ------------------------------------------------------------------

    async def enqueue(
        self,
        task_type: str,
        payload: dict,
        title: str = "",
        max_retries: int = 2,
    ) -> str:
        """Add a task to the queue. Returns task_id."""
        task_id = str(uuid.uuid4())[:8]
        now = time.time()

        conn = self._conn()
        conn.execute(
            """INSERT INTO tasks (id, type, status, payload, title, created_at, max_retries)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (task_id, task_type, TaskStatus.PENDING, json.dumps(payload),
             title or task_type, now, max_retries),
        )
        conn.commit()
        conn.close()
        return task_id

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    async def get(self, task_id: str) -> Task | None:
        """Get task by ID."""
        conn = self._conn()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_task(row)

    async def list_tasks(
        self,
        status: TaskStatus | None = None,
        task_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Task]:
        """List tasks with optional filters."""
        conn = self._conn()
        query = "SELECT * FROM tasks WHERE 1=1"
        params: list = []
        if status:
            query += " AND status = ?"
            params.append(status.value)
        if task_type:
            query += " AND type = ?"
            params.append(task_type)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = conn.execute(query, params).fetchall()
        conn.close()
        return [self._row_to_task(r) for r in rows]

    async def stats(self) -> dict:
        """Queue statistics."""
        conn = self._conn()
        rows = conn.execute(
            "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
        ).fetchall()
        conn.close()
        return {r["status"]: r["cnt"] for r in rows}

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def update_progress(self, task_id: str, progress: int, title: str = ""):
        """Update task progress (0-100)."""
        conn = self._conn()
        if title:
            conn.execute(
                "UPDATE tasks SET progress = ?, title = ? WHERE id = ?",
                (min(100, max(0, progress)), title, task_id),
            )
        else:
            conn.execute(
                "UPDATE tasks SET progress = ? WHERE id = ?",
                (min(100, max(0, progress)), task_id),
            )
        conn.commit()
        conn.close()

    async def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        conn = self._conn()
        cur = conn.execute(
            "UPDATE tasks SET status = ? WHERE id = ? AND status = ?",
            (TaskStatus.CANCELLED, task_id, TaskStatus.PENDING),
        )
        conn.commit()
        conn.close()
        return cur.rowcount > 0

    async def delete(self, task_id: str) -> bool:
        """Delete a task."""
        conn = self._conn()
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
        return cur.rowcount > 0

    async def clear(self, status: TaskStatus | None = None):
        """Clear tasks. If status given, only clear that status."""
        conn = self._conn()
        if status:
            conn.execute("DELETE FROM tasks WHERE status = ?", (status.value,))
        else:
            conn.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    async def run_worker(self, concurrency: int = 3, poll_interval: float = 2.0):
        """Run the task worker. Processes up to `concurrency` tasks in parallel."""
        self._running = True
        sem = asyncio.Semaphore(concurrency)

        while self._running:
            # Grab pending tasks
            conn = self._conn()
            rows = conn.execute(
                "SELECT id FROM tasks WHERE status = ? ORDER BY created_at ASC LIMIT ?",
                (TaskStatus.PENDING, concurrency),
            ).fetchall()
            conn.close()

            for row in rows:
                if not self._running:
                    break
                await sem.acquire()
                asyncio.create_task(self._process_task(row["id"], sem))

            await asyncio.sleep(poll_interval)

    async def process_one(self, task_id: str):
        """Process a single task immediately (for testing or inline execution)."""
        await self._process_task(task_id)

    def stop(self):
        """Stop the worker loop."""
        self._running = False

    async def _process_task(self, task_id: str, sem: asyncio.Semaphore | None = None):
        """Execute a single task."""
        try:
            conn = self._conn()
            # Claim the task
            cur = conn.execute(
                "UPDATE tasks SET status = ?, started_at = ? WHERE id = ? AND status = ?",
                (TaskStatus.RUNNING, time.time(), task_id, TaskStatus.PENDING),
            )
            conn.commit()
            if cur.rowcount == 0:
                return  # Already claimed by another worker

            row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
            conn.close()
            if not row:
                return

            task_type = row["type"]
            payload = json.loads(row["payload"])

            handler = self._handlers.get(task_type)
            if not handler:
                await self._fail_task(task_id, f"No handler for task type: {task_type}")
                return

            # Execute handler
            result = await handler(task_id, payload)

            # Mark completed
            conn = self._conn()
            conn.execute(
                "UPDATE tasks SET status = ?, result = ?, progress = 100, completed_at = ? WHERE id = ?",
                (TaskStatus.COMPLETED, json.dumps(result or {}), time.time(), task_id),
            )
            conn.commit()
            conn.close()

        except Exception as e:
            tb = traceback.format_exc()
            await self._handle_failure(task_id, str(e), tb)
        finally:
            if sem:
                sem.release()

    async def _fail_task(self, task_id: str, error: str):
        conn = self._conn()
        conn.execute(
            "UPDATE tasks SET status = ?, error = ?, completed_at = ? WHERE id = ?",
            (TaskStatus.FAILED, error, time.time(), task_id),
        )
        conn.commit()
        conn.close()

    async def _handle_failure(self, task_id: str, error: str, tb: str):
        """Handle task failure with retry logic."""
        conn = self._conn()
        row = conn.execute("SELECT retries, max_retries FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row and row["retries"] < row["max_retries"]:
            # Retry
            conn.execute(
                "UPDATE tasks SET status = ?, retries = retries + 1, error = ? WHERE id = ?",
                (TaskStatus.PENDING, f"{error}\n{tb}", task_id),
            )
        else:
            # Final failure
            conn.execute(
                "UPDATE tasks SET status = ?, error = ?, completed_at = ? WHERE id = ?",
                (TaskStatus.FAILED, f"{error}\n{tb}", time.time(), task_id),
            )
        conn.commit()
        conn.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _row_to_task(self, row) -> Task:
        return Task(
            id=row["id"],
            type=row["type"],
            status=TaskStatus(row["status"]),
            payload=json.loads(row["payload"]) if row["payload"] else {},
            result=json.loads(row["result"]) if row["result"] else None,
            error=row["error"],
            progress=row["progress"],
            title=row["title"],
            created_at=row["created_at"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            retries=row["retries"],
            max_retries=row["max_retries"],
        )


# ======================================================================
# Video Creator handlers (register when imported by web.py)
# ======================================================================

queue = TaskQueue(str(Path(__file__).parent / "tasks.db"))


@queue.handler("generate_script")
async def handle_generate_script(task_id: str, payload: dict) -> dict:
    """Generate a video script via Claude."""
    from agent import write_script
    await queue.update_progress(task_id, 10, "Generating script...")
    topic = payload.get("topic", "")
    tier = payload.get("tier", 1)
    result = write_script(topic, tier=tier)
    await queue.update_progress(task_id, 100, "Script ready")
    return result


@queue.handler("generate_video")
async def handle_generate_video(task_id: str, payload: dict) -> dict:
    """Create video via HeyGen MCP."""
    from heygen_mcp import create_video as mcp_create, get_video as mcp_get
    from web import build_video_prompt

    script = payload.get("script", "")
    title = payload.get("title", "Video")
    montage = payload.get("montage", {"preset": "tiktok_viral"})
    fmt = payload.get("format", "portrait")
    orientation = "portrait" if fmt == "portrait" else "landscape"

    await queue.update_progress(task_id, 5, "Sending to HeyGen...")

    prompt = build_video_prompt(script, title, montage)
    result = mcp_create(prompt, orientation=orientation)

    if "error" in result:
        raise RuntimeError(result["error"])

    video_id = result.get("video_id", "")
    await queue.update_progress(task_id, 20, f"HeyGen rendering: {video_id}")

    # Poll until done
    for i in range(60):  # max 10 minutes (60 * 10s)
        await asyncio.sleep(10)
        status_data = mcp_get(video_id)
        status = status_data.get("status", "unknown")
        progress = min(20 + i, 90)
        await queue.update_progress(task_id, progress, f"Rendering: {status}")

        if status == "completed":
            await queue.update_progress(task_id, 100, "Video ready!")
            return {
                "video_id": video_id,
                "video_url": status_data.get("video_url", ""),
                "thumbnail_url": status_data.get("thumbnail_url", ""),
                "duration": status_data.get("duration"),
                "title": title,
            }
        elif status in ("failed", "error"):
            raise RuntimeError(f"HeyGen failed: {status_data.get('failure_message', status)}")

    raise RuntimeError("HeyGen render timeout (10 min)")


@queue.handler("generate_ideas")
async def handle_generate_ideas(task_id: str, payload: dict) -> dict:
    from agent import generate_ideas
    await queue.update_progress(task_id, 10)
    result = generate_ideas(payload.get("topic", ""), count=payload.get("count", 5))
    return result


@queue.handler("batch_videos")
async def handle_batch_videos(task_id: str, payload: dict) -> dict:
    """Generate multiple videos from a list of topics."""
    topics = payload.get("topics", [])
    results = []
    for i, topic in enumerate(topics):
        sub_id = await queue.enqueue("generate_video", {
            "script": topic.get("script", ""),
            "title": topic.get("title", f"Video {i+1}"),
            "montage": payload.get("montage", {"preset": "tiktok_viral"}),
            "format": payload.get("format", "portrait"),
        }, title=topic.get("title", f"Video {i+1}"))
        results.append({"topic": topic.get("title"), "task_id": sub_id})
        progress = int((i + 1) / len(topics) * 100)
        await queue.update_progress(task_id, progress, f"Queued {i+1}/{len(topics)}")
    return {"queued": len(results), "sub_tasks": results}
