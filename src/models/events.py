from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EventType(str, Enum):
    SCREENSHOT = "SCREENSHOT"
    MOUSE_CLICK = "MOUSE_CLICK"
    MOUSE_DOUBLE_CLICK = "MOUSE_DOUBLE_CLICK"
    MOUSE_RIGHT_CLICK = "MOUSE_RIGHT_CLICK"
    MOUSE_DRAG = "MOUSE_DRAG"
    KEY_PRESS = "KEY_PRESS"
    KEY_COMBINATION = "KEY_COMBINATION"
    TEXT_INPUT = "TEXT_INPUT"
    SCROLL = "SCROLL"
    NAVIGATION = "NAVIGATION"
    WINDOW_SWITCH = "WINDOW_SWITCH"
    FILE_OPERATION = "FILE_OPERATION"


class MouseButton(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"


class ClickEvent(BaseModel):
    x: int = Field(..., description="X coordinate in pixels")
    y: int = Field(..., description="Y coordinate in pixels")
    button: MouseButton = MouseButton.LEFT
    element_text: Optional[str] = Field(None, description="Text of clicked element if available")
    element_type: Optional[str] = Field(None, description="Type of element (button, link, input, etc)")


class DragEvent(BaseModel):
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    button: MouseButton = MouseButton.LEFT


class KeyPressEvent(BaseModel):
    key: str = Field(..., description="Key pressed (e.g., 'Enter', 'Tab', 'a')")
    modifiers: List[str] = Field(default_factory=list, description="Modifier keys held (ctrl, alt, shift)")


class TextInputEvent(BaseModel):
    text: str = Field(..., description="Text that was typed")
    target_element: Optional[str] = Field(None, description="Description of input field")


class ScrollEvent(BaseModel):
    x: int = Field(..., description="X position of scroll")
    y: int = Field(..., description="Y position of scroll")
    delta_x: int = Field(0, description="Horizontal scroll amount")
    delta_y: int = Field(..., description="Vertical scroll amount (negative = up)")


class NavigationEvent(BaseModel):
    url: str = Field(..., description="URL navigated to")
    title: Optional[str] = Field(None, description="Page title")


class WindowSwitchEvent(BaseModel):
    window_title: str
    application: Optional[str] = None


class ScreenshotEvent(BaseModel):
    s3_key: str = Field(..., description="S3 key where screenshot is stored")
    width: int
    height: int
    ocr_text: Optional[str] = Field(None, description="Extracted text from screenshot")


class EventLog(BaseModel):
    timestamp: datetime
    event_type: EventType
    data: Any = Field(..., description="Event-specific data")
    screenshot_ref: Optional[str] = Field(None, description="Reference to associated screenshot S3 key")
    
    class Config:
        use_enum_values = True


class SessionTimeline(BaseModel):
    session_id: str
    user_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    application: str = Field(..., description="Primary application being recorded")
    events: List[EventLog] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    
    class Config:
        use_enum_values = True