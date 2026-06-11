from pydantic import BaseModel, Field


class LensConfig(BaseModel):
    name: str
    objective: str


class TraceConfig(BaseModel):
    id: str
    severity: str = Field(pattern="^(low|medium|high)$")


class ThreadmereFixture(BaseModel):
    scenario: str
    lens: LensConfig
    traces: list[TraceConfig]
