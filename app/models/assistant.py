from typing import Any

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class ExecutionStep(BaseModel):
    step: str
    detail: str


class AssistantResponse(BaseModel):
    answer: str
    intent: str
    data: dict[str, Any] = Field(default_factory=dict)
    execution_steps: list[ExecutionStep] = Field(default_factory=list)
