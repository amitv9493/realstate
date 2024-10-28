from dataclasses import dataclass


@dataclass
class NotificationTemplate:
    title: str
    body: str
    body2: str


@dataclass
class NotificationMetaData:
    title: str
    body: str
    data: dict
    device_id: str


class NotificationTemplates:
    JOB_NOT_ACCEPTED_YET = NotificationTemplate(
        title="Your Job is Still pending",
        body=(
            "Reminder: Your job {type_of_task} hasn't been accepted yet. "
            "Consider adjusting details or payment to attract agents."
        ),
        body2="",
    )
    CREATED = NotificationTemplate(
        title="Job Created",
        body="Your job {type_of_task} has been posted successfully and is now visible to agents.",
        body2="",
    )
    ASSIGNED = NotificationTemplate(
        title="Job Accepted",
        body="Great news! {agent_name} has accepted your job {type_of_task}.",
        body2="You have successfully accepted the job {type_of_task} scheduled for {task_time}.",
    )
    STARTED = NotificationTemplate(
        title="Job Started",
        body="Your job {type_of_task} has been started by {agent_name} at {now}.",
        body2="You have started the task {type_of_task}",
    )
    MARK_COMPLETED = NotificationTemplate(
        title="Job Marked Completed",
        body=(
            "{agent_name} has marked your job {type_of_task} as completed."
            "Please review and confirm."
        ),
        body2=(
            "You have marked the job {type_of_task} as completed."
            "Awaiting confirmation from the job creator."
        ),
    )
    VERIFIED = NotificationTemplate(
        title="Job Completed",
        body=(
            "You have confirmed the completion of '{type_of_task}."
            "Thank you for using our service!"
        ),
        body2="",
    )
    DETAILS_UPDATED = NotificationTemplate(
        title="Job Details Updated",
        body="You have updated {type_of_task}. Assigned agents have been notified of the changes.",
        body2="The job {type_of_task} has been updated. Please review the new details.",
    )

    ASSIGNER_CANCELLED = NotificationTemplate(
        title="Job Cancelled",
        body=(
            "Unfortunately, {agent_name} has canceled your job {type_of_task}."
            "It's now available for other agents."
        ),
        body2="You have withdrawn for the job {type_of_task}",
    )
    CREATER_CANCELLED = NotificationTemplate(
        title="Job Cancelled",
        body="You have canceled you job {type_of_task}.",
        body2="The job {type_of_task} scheduled for {task_time} has been canceled by the creator.",
    )
    REASSIGNED = NotificationTemplate(
        title="Job Reassigned",
        body="You job {type_of_task} has been reassigned to {agent_name}.",
        body2="",
    )
    REMINDER_24 = NotificationTemplate(
        title="Scheduled time approaching",
        body="Reminder: Your job {type_of_task} is scheduled for tomorrow at {task_time}.",
        body2="Reminder: You have the job {type_of_task} tomorrow at {task_time}.",
    )
    REMINDER_1 = NotificationTemplate(
        title="Scheduled time imminent",
        body="Reminder: Your job {type_of_task} starts in 1 hour.",
        body2="Reminder: The job {type_of_task} starts in 1 hour.",
    )


def get_notification_template(event_type, **kwargs):
    template = getattr(NotificationTemplates, event_type)
    return (
        template.title,
        template.body.format(
            type_of_task=kwargs.get("type_of_task", ""),
            agent_name=kwargs.get("agent_name", ""),
            now=kwargs.get("now", ""),
            task_time=kwargs.get("task_time", ""),
        ),
        template.body2.format(
            type_of_task=kwargs.get("type_of_task", ""),
            agent_name=kwargs.get("agent_name", ""),
            now=kwargs.get("now", ""),
            task_time=kwargs.get("task_time", ""),
        ),
    )
