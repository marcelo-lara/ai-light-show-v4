from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health")
def get_health() -> dict[str, bool]:
    return {"ok": True}
