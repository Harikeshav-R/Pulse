from pydantic import BaseModel


class AlertUpdateRequest(BaseModel):
    action: str  # acknowledge, resolve, dismiss, escalate
    note: str | None = None
