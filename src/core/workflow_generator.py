import json
import uuid
from datetime import datetime
from typing import Optional

from src.models.events import SessionTimeline, EventType
from src.models.workflow import WorkflowDefinition, WorkflowStep, ActionType, Selector
from src.services.bedrock_client import BedrockClient


class WorkflowGenerator:
    def __init__(self, bedrock_client: Optional[BedrockClient] = None):
        self.bedrock = bedrock_client or BedrockClient()
    
    def generate_from_session(self, session: SessionTimeline) -> WorkflowDefinition:
        """Generate a workflow definition from a recorded session"""
        
        # Convert session to dict for Bedrock
        session_dict = session.model_dump(mode="json")
        
        # Get AI-generated workflow
        ai_response = self.bedrock.generate_workflow(session_dict, [])
        
        # Parse and validate the response
        workflow_json = self._extract_json(ai_response)
        workflow = WorkflowDefinition(**workflow_json)
        
        return workflow
    
    def generate_from_events_only(self, session: SessionTimeline) -> WorkflowDefinition:
        """Generate workflow using only event logs (no AI, deterministic)"""
        
        steps = []
        step_counter = 1
        
        for event in session.events:
            step = self._event_to_step(event, step_counter)
            if step:
                steps.append(step)
                step_counter += 1
        
        workflow = WorkflowDefinition(
            workflow_id=str(uuid.uuid4()),
            name=f"Workflow from {session.session_id}",
            description=f"Auto-generated workflow from session recording",
            application=session.application,
            steps=steps,
            metadata={
                "source_session": session.session_id,
                "generated_at": datetime.utcnow().isoformat(),
                "event_count": len(session.events)
            }
        )
        
        return workflow
    
    def _event_to_step(self, event, step_num: int) -> Optional[WorkflowStep]:
        """Convert a single event log to a workflow step"""
        
        event_type = event.event_type
        data = event.data
        
        if event_type == EventType.MOUSE_CLICK:
            return WorkflowStep(
                step_id=f"step_{step_num}",
                action=ActionType.CLICK,
                description=f"Click at ({data.get('x')}, {data.get('y')})",
                selector=Selector(
                    type="coordinates",
                    value={"x": data.get("x"), "y": data.get("y")}
                ),
                parameters={"button": data.get("button", "left")},
                screenshot_before=event.screenshot_ref
            )
        
        elif event_type == EventType.MOUSE_DOUBLE_CLICK:
            return WorkflowStep(
                step_id=f"step_{step_num}",
                action=ActionType.DOUBLE_CLICK,
                description=f"Double-click at ({data.get('x')}, {data.get('y')})",
                selector=Selector(
                    type="coordinates",
                    value={"x": data.get("x"), "y": data.get("y")}
                ),
                parameters={}
            )
        
        elif event_type == EventType.TEXT_INPUT:
            return WorkflowStep(
                step_id=f"step_{step_num}",
                action=ActionType.TYPE_TEXT,
                description=f"Type: {data.get('text', '')[:50]}...",
                selector=None,
                parameters={"text": data.get("text", "")}
            )
        
        elif event_type == EventType.KEY_PRESS:
            return WorkflowStep(
                step_id=f"step_{step_num}",
                action=ActionType.PRESS_KEY,
                description=f"Press key: {data.get('key')}",
                selector=None,
                parameters={
                    "key": data.get("key"),
                    "modifiers": data.get("modifiers", [])
                }
            )
        
        elif event_type == EventType.SCROLL:
            return WorkflowStep(
                step_id=f"step_{step_num}",
                action=ActionType.SCROLL,
                description=f"Scroll by ({data.get('delta_x', 0)}, {data.get('delta_y', 0)})",
                selector=Selector(
                    type="coordinates",
                    value={"x": data.get("x"), "y": data.get("y")}
                ),
                parameters={
                    "delta_x": data.get("delta_x", 0),
                    "delta_y": data.get("delta_y", 0)
                }
            )
        
        elif event_type == EventType.NAVIGATION:
            return WorkflowStep(
                step_id=f"step_{step_num}",
                action=ActionType.NAVIGATE,
                description=f"Navigate to {data.get('url', '')}",
                selector=None,
                parameters={"url": data.get("url", "")}
            )
        
        elif event_type == EventType.SCREENSHOT:
            # Screenshots are reference points, not actions
            return None
        
        return None
    
    def _extract_json(self, text: str) -> dict:
        """Extract JSON from AI response text"""
        
        # Try to find JSON in the response
        text = text.strip()
        
        # If wrapped in code blocks, extract
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            text = text[start:end].strip()
        
        # Parse JSON
        return json.loads(text)