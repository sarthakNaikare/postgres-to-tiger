from fastapi import APIRouter, HTTPException
from utils.session_store import get_session

router = APIRouter()


@router.get("/status/{session_id}")
def get_benchmark_status(session_id: str):
    """
    Poll this endpoint every few seconds while benchmark is running.
    Returns current stage and progress percentage.
    """
    session = get_session(session_id)

    if session is None:
        raise HTTPException(
            status_code=404,
            detail=f"Session {session_id} not found"
        )

    return session
