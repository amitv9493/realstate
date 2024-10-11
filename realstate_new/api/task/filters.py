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
        lookup_expr="date__gte",
    )
    task_time_lte = django_filters.DateTimeFilter(
        field_name="task_time",
        lookup_expr="date__lte",
    )
    task_time = django_filters.DateTimeFilter(
        field_name="task_time",
        lookup_expr="date__exact",
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


select_related = {
    "LockBoxBS": ["pickup_address", "installation_or_remove_address"],
    "LockBoxIR": ["pickup_address"],
    "Showing": ["property"],
    "OpenHouse": ["property"],
    "Runner": ["pickup_address", "dropoff_address"],
    "Sign": [
        "install_address",
        "pickup_address",
        "remove_address",
        "dropoff_address",
    ],
    "Professional": ["property"],
}


def filter_tasks(request, base_query):
    filtered_tasks = {}
    type_of_task = request.query_params.get("type_of_task", "")
    if type_of_task:
        type_of_task_list = [t.strip() for t in type_of_task.split(",")]
    else:
        type_of_task_list = list(JOB_TYPE_MAPPINGS.keys())
    for task_type in type_of_task_list:
        queryset = (
            JOB_TYPE_MAPPINGS[task_type]
            .objects.filter(base_query)
            .select_related(*select_related[task_type])
        )
        task_filter = TaskFilter(
            request.query_params,
            queryset=queryset,
            request=request,
        )
        filtered_tasks[task_type] = task_filter
    return filtered_tasks
