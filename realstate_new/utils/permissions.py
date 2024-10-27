from typing import Any

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from realstate_new.task.models.choices import TaskStatusChoices


class AssigneeObjectPermission(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        assignee_actions = [
            TaskStatusChoices.STARTED,
            TaskStatusChoices.MARK_COMPLETED,
            TaskStatusChoices.ASSIGNER_CANCELLED,
        ]
        if request.task_action in assignee_actions:
            if request.user != obj.assigned_to:
                return False

        return True
