from pydantic import BaseModel, Field


class ScenarioTurn(BaseModel):
    turn_id: int = Field(ge=1)
    user_message: str = Field(min_length=1)
    assistant_response: str = Field(min_length=1)
    inspected_artifacts: list[str] = Field(default_factory=list)
    retrieved_artifacts: list[str] = Field(default_factory=list)
    memory_write_requested: bool = False
    notes: str = ""


class ThreadmereScenario(BaseModel):
    scenario_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    domain_pack: str = Field(min_length=1)
    learner_role: str = Field(min_length=1)
    assistant_profile: str = Field(min_length=1)
    available_artifacts: list[str] = Field(min_length=1)
    trusted_sources: list[str] = Field(default_factory=list)
    untrusted_sources: list[str] = Field(default_factory=list)
    active_policies: list[str] = Field(default_factory=list)
    hidden_risks: list[str] = Field(default_factory=list)
    starting_context: str = Field(min_length=1)
    allowed_actions: list[str] = Field(default_factory=list)
    success_conditions: list[str] = Field(default_factory=list)
    failure_conditions: list[str] = Field(default_factory=list)
    expected_lens_events: list[str] = Field(default_factory=list)
    debrief_goals: list[str] = Field(default_factory=list)
    ethical_use_boundary: str = ""
    briefing: str = ""
    scripted_turns: list[ScenarioTurn] = Field(default_factory=list)
