import threading
import time

# In-memory store — maps session_id to its current status
# This is fine for a single-server deployment
_store = {}
_lock = threading.Lock()


def create_session(session_id: str):
    """Called when a benchmark session starts."""
    with _lock:
        _store[session_id] = {
            "session_id": session_id,
            "status": "starting",
            "stage": "Spinning up containers...",
            "progress_percent": 0,
            "started_at": time.time(),
            "error": None
        }


def update_session(session_id: str, stage: str, progress_percent: int):
    """Called as the benchmark moves through stages."""
    with _lock:
        if session_id in _store:
            _store[session_id]["stage"] = stage
            _store[session_id]["progress_percent"] = progress_percent
            _store[session_id]["status"] = "running"


def complete_session(session_id: str):
    """Called when benchmark finishes successfully."""
    with _lock:
        if session_id in _store:
            _store[session_id]["status"] = "complete"
            _store[session_id]["progress_percent"] = 100
            _store[session_id]["stage"] = "Done!"


def fail_session(session_id: str, error: str):
    """Called when benchmark fails."""
    with _lock:
        if session_id in _store:
            _store[session_id]["status"] = "failed"
            _store[session_id]["error"] = error


def get_session(session_id: str) -> dict:
    """Returns current status of a session."""
    with _lock:
        return _store.get(session_id, None)


def cleanup_old_sessions():
    """
    Removes sessions older than 10 minutes from memory.
    Called by the watchdog periodically.
    """
    now = time.time()
    with _lock:
        to_delete = [
            sid for sid, data in _store.items()
            if now - data["started_at"] > 600  # 10 minutes
        ]
        for sid in to_delete:
            del _store[sid]
