from typing import Literal

from pydantic import BaseModel, Field

from schemas.event_types import EventType


class ReplayframeEvent(BaseModel):
    turn_id: int = Field(ge=1)
    event_type: EventType
    severity: Literal["low", "medium", "high"]
    explanation: str = Field(min_length=1)
    source: str = ""
    lens: str = ""


class ReplayframeTrace(BaseModel):
    timeline_id: str = Field(min_length=1)
    events: list[ReplayframeEvent]
