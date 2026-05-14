from fastapi import APIRouter

router = APIRouter(tags=["search"])


@router.get("/ping")
def search_ping() -> dict:
    return {"ok": True}
