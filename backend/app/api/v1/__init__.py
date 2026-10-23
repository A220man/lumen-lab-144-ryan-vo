from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def api_health():
    return {"status": "ok", "version": "1.0.0"}