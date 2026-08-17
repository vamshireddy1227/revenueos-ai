from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import Workflow, WorkflowRun, Notification

class WorkflowEngineService:
    """
    Trigger-Action Workflow Automation Engine.
    Executes automated tasks (notifications, lead score updates, ticket routing) when events trigger.
    """

    def trigger_event(self, db: Session, organization_id: str, event_name: str, payload: Dict[str, Any]):
        """Find matching workflows for event and execute action steps."""
        workflows = db.query(Workflow).filter(
            Workflow.organization_id == organization_id,
            Workflow.trigger_event == event_name,
            Workflow.is_active == True
        ).all()

        for wf in workflows:
            logs = []
            logs.append(f"Workflow '{wf.name}' triggered by event '{event_name}'.")
            
            # Execute step actions
            for step in (wf.actions_json or []):
                action_type = step.get("type", "")
                if action_type == "send_notification":
                    title = step.get("title", f"Workflow Alert: {event_name}")
                    msg = step.get("message", f"Event {event_name} occurred with payload {payload}")
                    notif = Notification(
                        organization_id=organization_id,
                        user_id=payload.get("user_id"),
                        title=title,
                        message=msg,
                        priority=step.get("priority", "normal"),
                        type="workflow_alert"
                    )
                    db.add(notif)
                    logs.append(f"Notification sent: {title}")
                elif action_type == "log":
                    logs.append(f"Action Log: {step.get('text', '')}")

            run = WorkflowRun(
                workflow_id=wf.id,
                organization_id=organization_id,
                status="success",
                logs_json=logs
            )
            db.add(run)
            db.commit()

workflow_engine = WorkflowEngineService()
