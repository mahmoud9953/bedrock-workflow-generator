from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    CLICK = "CLICK"
    DOUBLE_CLICK = "DOUBLE_CLICK"
    RIGHT_CLICK = "RIGHT_CLICK"
    TYPE_TEXT = "TYPE_TEXT"
    PRESS_KEY = "PRESS_KEY"
    KEY_COMBINATION = "KEY_COMBINATION"
    SCROLL = "SCROLL"
    DRAG = "DRAG"
    WAIT = "WAIT"
    NAVIGATE = "NAVIGATE"
    SWITCH_WINDOW = "SWITCH_WINDOW"
    CONDITIONAL = "CONDITIONAL"
    LOOP = "LOOP"


class Selector(BaseModel):
    """How to identify a UI element"""
    type: str = Field(..., description="Selector type: coordinates, text, xpath, css, image")
    value: Any = Field(..., description="Selector value")
    fallback: Optional["Selector"] = Field(None, description="Fallback selector if primary fails")


class WorkflowStep(BaseModel):
    step_id: str
    action: ActionType
    description: str = Field(..., description="Human-readable description of this step")
    selector: Optional[Selector] = Field(None, description="How to find target element")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Action-specific parameters")
    screenshot_before: Optional[str] = Field(None, description="Expected screen state before action")
    screenshot_after: Optional[str] = Field(None, description="Expected screen state after action")
    wait_after: float = Field(0.5, description="Seconds to wait after action")
    retry_count: int = Field(3, description="Number of retries on failure")
    on_failure: str = Field("stop", description="What to do on failure: stop, skip, retry")


class WorkflowDefinition(BaseModel):
    workflow_id: str
    name: str
    description: str
    version: str = "1.0.0"
    application: str = Field(..., description="Target application for this workflow")
    steps: List[WorkflowStep]
    variables: Dict[str, Any] = Field(default_factory=dict, description="Workflow variables")
    preconditions: List[str] = Field(default_factory=list, description="Required conditions before running")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# Fix forward reference
Selector.model_rebuild()