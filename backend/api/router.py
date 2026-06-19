# backend/api/router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.engine import ArtWebEngine

router = APIRouter()
engine = ArtWebEngine()

class PurchaseRequest(BaseModel):
    user_id: str
    tier: str
    deity_id: int
    shards: int

@router.get("/assets")
async def list_all_assets():
    return engine.asset_registry

@router.get("/assets/{deity_id}")
async def get_single_asset(deity_id: int):
    if deity_id not in engine.asset_registry:
        raise HTTPException(status_code=404, detail="Deity not found.")
    return engine.asset_registry[deity_id]

@router.post("/purchase")
async def execute_art_purchase(request: PurchaseRequest):
    result = engine.process_purchase(
        user_id=request.user_id,
        tier=request.tier,
        deity_id=request.deity_id,
        shards=request.shards
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
