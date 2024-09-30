import django_filters

from realstate_new.master.models.types import JOB_TYPE_MAPPINGS
from realstate_new.task.models import ShowingTask


class TaskFilter(django_filters.FilterSet):
    min_payment = django_filters.NumberFilter(
        field_name="payment_amount",
        lookup_expr="gte",
    )
    max_payment = django_filters.NumberFilter(
        field_name="payment_amount",
        lookup_expr="lte",
    )
    payment = django_filters.NumberFilter(
        field_name="payment_amount",
        lookup_expr="exact",
    )
    task_time_gte = django_filters.DateTimeFilter(
        field_name="task_time",
        lookup_expr="gte",
    )
    task_time_lte = django_filters.DateTimeFilter(
        field_name="task_time",
        lookup_expr="lte",
    )
    task_time = django_filters.DateTimeFilter(
        field_name="task_time",
        lookup_expr="exact",
    )
    asap = django_filters.BooleanFilter(method="filter_asap")

    class Meta:
        model = ShowingTask
        fields = [
            "min_payment",
            "max_payment",
            "payment",
            "task_time_gte",
            "task_time_lte",
            "task_time",
            "asap",
        ]

    def filter_asap(self, queryset, name, value):
        if value:
            return queryset.filter(asap=True).order_by("task_time")
        return queryset

    @property
    def qs(self):
        parent = super().qs
        user = getattr(self.request, "user", None)

        if user and user.is_authenticated:
            if self.data.get("flag") == "latest":
                return parent.exclude(applications__applicant=user)
        return parent


def filter_tasks(request, base_query):
    filtered_tasks = {}
    for task_type, task_model in JOB_TYPE_MAPPINGS.items():
        queryset = task_model.objects.filter(**base_query)
        filtered_tasks[task_type] = TaskFilter(
            request.query_params,
            queryset=queryset,
            request=request,
        )

    return filtered_tasks
