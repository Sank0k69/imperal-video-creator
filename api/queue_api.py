"""Task queue endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from taskqueue import queue, TaskStatus

router = APIRouter(prefix="/api/queue", tags=["queue"])


@router.post("/enqueue")
async def enqueue(req: Request):
    body = await req.json()
    task_type = body.get("type", "")
    payload = body.get("payload", {})
    title = body.get("title", "")
    if not task_type:
        return JSONResponse({"ok": False, "error": "type is required"}, status_code=400)
    task_id = await queue.enqueue(task_type, payload, title=title)
    return JSONResponse({"ok": True, "task_id": task_id})


@router.get("/tasks")
async def list_tasks(status: str = "", task_type: str = "", limit: int = 50):
    s = TaskStatus(status) if status else None
    tasks = await queue.list_tasks(status=s, task_type=task_type or None, limit=limit)
    return JSONResponse({"ok": True, "tasks": [
        {"id": t.id, "type": t.type, "status": t.status.value, "title": t.title,
         "progress": t.progress, "result": t.result, "error": t.error,
         "created_at": t.created_at, "completed_at": t.completed_at}
        for t in tasks
    ]})


@router.get("/task/{task_id}")
async def get_task(task_id: str):
    t = await queue.get(task_id)
    if not t:
        return JSONResponse({"ok": False, "error": "Task not found"}, status_code=404)
    return JSONResponse({"ok": True, "task": {
        "id": t.id, "type": t.type, "status": t.status.value, "title": t.title,
        "progress": t.progress, "payload": t.payload, "result": t.result,
        "error": t.error, "created_at": t.created_at, "started_at": t.started_at,
        "completed_at": t.completed_at, "retries": t.retries,
    }})


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    return JSONResponse({"ok": await queue.delete(task_id)})


@router.post("/cancel/{task_id}")
async def cancel_task(task_id: str):
    return JSONResponse({"ok": await queue.cancel(task_id)})


@router.get("/stats")
async def stats():
    return JSONResponse({"ok": True, "stats": await queue.stats()})
