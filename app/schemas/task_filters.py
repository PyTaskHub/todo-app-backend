from enum import Enum


class TaskSortBy(str, Enum):
    created_at = "created_at"
    priority = "priority"
    due_date = "due_date"
    status = "status"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class StatusFilter(str, Enum):
    all = "all"
    pending = "pending"
    completed = "completed"
