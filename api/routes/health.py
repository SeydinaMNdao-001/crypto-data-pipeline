from fastapi import APIRouter, HTTPException

from src.utils.db import get_connection

router = APIRouter()


@router.get("/health")
def health_check():
    """Vérifie que l'API ET sa base de données sont opérationnelles."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Base de données inaccessible: {exc}")
    return {"status": "ok"}
