import json
from datetime import datetime, timedelta
from src.models.events import SessionTimeline, EventLog, EventType
from src.core.workflow_generator import WorkflowGenerator


def create_mock_session():
    """Create a mock recording session - user logging into a website"""
    
    start_time = datetime.utcnow()
    
    session = SessionTimeline(
        session_id="test-session-001",
        user_id="demo-user",
        start_time=start_time,
        application="Chrome Browser",
        events=[
            # Step 1: Click on username field
            EventLog(
                timestamp=start_time + timedelta(seconds=1),
                event_type=EventType.MOUSE_CLICK,
                data={
                    "x": 450,
                    "y": 320,
                    "button": "left",
                    "element_text": "Username",
                    "element_type": "input"
                },
                screenshot_ref="screenshots/step_001.png"
            ),
            # Step 2: Type username
            EventLog(
                timestamp=start_time + timedelta(seconds=2),
                event_type=EventType.TEXT_INPUT,
                data={
                    "text": "demo@example.com",
                    "target_element": "username input field"
                }
            ),
            # Step 3: Click on password field
            EventLog(
                timestamp=start_time + timedelta(seconds=4),
                event_type=EventType.MOUSE_CLICK,
                data={
                    "x": 450,
                    "y": 380,
                    "button": "left",
                    "element_text": "Password",
                    "element_type": "input"
                },
                screenshot_ref="screenshots/step_003.png"
            ),
            # Step 4: Type password
            EventLog(
                timestamp=start_time + timedelta(seconds=5),
                event_type=EventType.TEXT_INPUT,
                data={
                    "text": "SecurePass123!",
                    "target_element": "password input field"
                }
            ),
            # Step 5: Click login button
            EventLog(
                timestamp=start_time + timedelta(seconds=7),
                event_type=EventType.MOUSE_CLICK,
                data={
                    "x": 450,
                    "y": 450,
                    "button": "left",
                    "element_text": "Login",
                    "element_type": "button"
                },
                screenshot_ref="screenshots/step_005.png"
            ),
            # Step 6: Page navigation after login
            EventLog(
                timestamp=start_time + timedelta(seconds=9),
                event_type=EventType.NAVIGATION,
                data={
                    "url": "https://app.example.com/dashboard",
                    "title": "Dashboard - Example App"
                }
            )
        ],
        metadata={
            "recording_tool": "workflow-recorder-v1",
            "os": "Windows 11",
            "screen_resolution": "1920x1080"
        }
    )
    
    return session


def test_deterministic_generation():
    """Test workflow generation without AI (pure event conversion)"""
    
    print("=" * 60)
    print("TEST: Deterministic Workflow Generation (No AI)")
    print("=" * 60)
    
    session = create_mock_session()
    generator = WorkflowGenerator()
    
    workflow = generator.generate_from_events_only(session)
    
    print(f"\nGenerated Workflow:")
    print(f"  ID: {workflow.workflow_id}")
    print(f"  Name: {workflow.name}")
    print(f"  Application: {workflow.application}")
    print(f"  Steps: {len(workflow.steps)}")
    
    print("\nWorkflow Steps:")
    for step in workflow.steps:
        print(f"  {step.step_id}: {step.action} - {step.description}")
    
    print("\nFull JSON Output:")
    print(json.dumps(workflow.model_dump(), indent=2, default=str))
    
    return workflow


def test_ai_generation():
    """Test workflow generation with Nova Pro AI"""
    
    print("\n" + "=" * 60)
    print("TEST: AI-Powered Workflow Generation (Nova Pro)")
    print("=" * 60)
    
    session = create_mock_session()
    generator = WorkflowGenerator()
    
    print("\nSending session to Nova Pro for analysis...")
    
    try:
        workflow = generator.generate_from_session(session)
        
        print(f"\nAI Generated Workflow:")
        print(f"  ID: {workflow.workflow_id}")
        print(f"  Name: {workflow.name}")
        print(f"  Description: {workflow.description}")
        print(f"  Steps: {len(workflow.steps)}")
        
        print("\nFull JSON Output:")
        print(json.dumps(workflow.model_dump(), indent=2, default=str))
        
        return workflow
        
    except Exception as e:
        print(f"\nAI generation failed: {e}")
        return None


if __name__ == "__main__":
    # Test 1: No AI
    workflow1 = test_deterministic_generation()
    
    # Test 2: With AI
    workflow2 = test_ai_generation()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)