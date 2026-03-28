from pydantic import BaseModel


class WearableReadingItem(BaseModel):
    metric: str
    value: float
    recorded_at: str
    source: str | None = None
    quality: str = "raw"


class WearableSyncRequest(BaseModel):
    readings: list[WearableReadingItem]


class WearableSyncResponse(BaseModel):
    accepted: int
    rejected: int
