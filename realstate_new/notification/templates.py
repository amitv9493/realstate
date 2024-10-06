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
            "Reminder: Your job {job_title} hasn't been accepted yet. "
            "Consider adjusting details or payment to attract agents."
        ),
        body2="",
    )
    CREATED = NotificationTemplate(
        title="Job Created",
        body="Your job {job_title} has been posted successfully and is now visible to agents.",
        body2="",
    )
    ASSIGNED = NotificationTemplate(
        title="Job Accepted",
        body="Great news! {agent_name} has accepted your job {job_title}.",
        body2="You have successfully accepted the job {job_title} scheduled for {task_time}.",
    )
    STARTED = NotificationTemplate(
        title="Job Started",
        body="Your job {job_title} has been started by {agent_name} at {now}.",
        body2="",
    )
    COMPLETED = NotificationTemplate(
        title="Job Completed",
        body="Your job {job_title} has been marked completed by {agent_name} at {now}.",
        body2="",
    )
    DETAILS_UPDATED = NotificationTemplate(
        title="Job Details Updated",
        body="You have updated {job_title}. Assigned agents have been notified of the changes.",
        body2="The job {job_title} has been updated. Please review the new details.",
    )

    ASSIGNER_CANCELLED = NotificationTemplate(
        title="Job Cancelled",
        body=(
            "Unfortunately, {agent_name} has canceled your job {job_title}."
            "It's now available for other agents."
        ),
        body2="You have withdrawn for the job {job_title}",
    )
    CREATER_CANCELLED = NotificationTemplate(
        title="Job Cancelled",
        body="You have canceled you job {job_title}.",
        body2="The job {job_title} scheduled for {task_time} has been canceled by the creator.",
    )
    REASSIGNED = NotificationTemplate(
        title="Job Reassigned",
        body="You job {job_title} has been reassigned to {agent_name}.",
        body2="",
    )
    REMINDER_24 = NotificationTemplate(
        title="Scheduled time approaching",
        body="Reminder: Your job {job_title} is scheduled for tomorrow at {task_time}.",
        body2="Reminder: You have the job {job_title} tomorrow at {task_time}.",
    )
    REMINDER_1 = NotificationTemplate(
        title="Scheduled time imminent",
        body="Reminder: Your job {job_title} starts in 1 hour.",
        body2="Reminder: The job {job_title} starts in 1 hour.",
    )


def get_notification_template(
    event_type,
    job_title,
    agent_name: str | None = None,
    now: str | None = None,
    task_time: str | None = None,
):
    template = getattr(NotificationTemplates, event_type)
    return (
        template.title,
        template.body.format(
            job_title=job_title,
            agent_name=agent_name,
            now=now,
            task_time=task_time,
        ),
        template.body2.format(
            job_title=job_title,
            agent_name=agent_name,
            now=now,
            task_time=task_time,
        ),
    )
