from datetime import date
from typing import Optional, List, Dict, Set


DEFAULT_WEIGHTS: Dict[str, float] = {
    "urgency": 0.4,
    "importance": 0.3,
    "effort": 0.2,
    "dependency": 0.1,
}


def calculate_urgency(due_date: Optional[date]) -> int:
    """
    Convert due_date into a 0–10 urgency score.
    Handles overdue tasks specially.
    """
    if not due_date:
        return 3  # low/neutral urgency if no due date

    today = date.today()
    days_left = (due_date - today).days

    if days_left < 0:
        return 10  # overdue – highest urgency
    if days_left == 0:
        return 9   # due today
    if days_left <= 3:
        return 8
    if days_left <= 7:
        return 6
    if days_left <= 14:
        return 4
    return 2  # far in future


def calculate_effort_score(estimated_hours: Optional[float]) -> int:
    """
    Lower effort = higher score (quick wins).
    """
    if estimated_hours is None:
        return 5  # neutral

    if estimated_hours <= 1:
        return 10  # super quick
    if estimated_hours <= 3:
        return 8
    if estimated_hours <= 6:
        return 5
    if estimated_hours <= 10:
        return 3

    return 1  # very heavy


def calculate_dependency_score(task_id: Optional[int], all_tasks: List[Dict]) -> int:
    """
    Tasks that block more other tasks get a higher score.
    """
    if task_id is None:
        return 0

    block_count = 0
    for t in all_tasks:
        deps = t.get("dependencies") or []
        if task_id in deps:
            block_count += 1

    # each blocked task adds 2 points, cap at 10
    return min(block_count * 2, 10)


def detect_cycles(tasks: List[Dict]) -> Set[int]:
    """
    Detect circular dependencies in the given list of tasks.

    Returns: set of task IDs that are part of at least one cycle.
    """
    graph: Dict[int, List[int]] = {}
    for t in tasks:
        tid = t.get("id")
        deps = t.get("dependencies") or []
        if tid is not None:
            graph[tid] = deps

    in_cycle: Set[int] = set()
    visited: Set[int] = set()
    stack: Set[int] = set()

    def dfs(node: int) -> None:
        if node in stack:
            # found a cycle, mark everything currently in stack
            in_cycle.update(stack)
            return
        if node in visited:
            return

        visited.add(node)
        stack.add(node)
        for neigh in graph.get(node, []):
            dfs(neigh)
        stack.remove(node)

    for node in graph.keys():
        if node not in visited:
            dfs(node)

    return in_cycle


def score_task(
    task: Dict,
    all_tasks: List[Dict],
    strategy: str = "smart_balance",
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Main scoring function.

    strategy:
      - "fastest_wins": favor low effort
      - "high_impact": favor importance and dependencies
      - "deadline_driven": favor urgency
      - "smart_balance": mix of all (default)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    urgency = calculate_urgency(task.get("due_date"))
    importance = task.get("importance", 5)
    effort_score = calculate_effort_score(task.get("estimated_hours"))
    dependency_score = calculate_dependency_score(task.get("id"), all_tasks)

    if strategy == "fastest_wins":
        # heavily favor quick wins, but still consider urgency a bit
        score = effort_score * 1.5 + urgency * 0.5
    elif strategy == "high_impact":
        # importance + being a blocker is king
        score = importance * 1.2 + dependency_score * 1.3
    elif strategy == "deadline_driven":
        # due date matters much more
        score = urgency * 2 + importance * 0.5
    else:
        # smart_balance (default)
        score = (
            urgency * weights["urgency"]
            + importance * weights["importance"]
            + effort_score * weights["effort"]
            + dependency_score * weights["dependency"]
        )

    return round(float(score), 2)


def build_explanation(
    task: Dict,
    all_tasks: List[Dict],
    strategy: str,
    cycles: Set[int],
) -> str:
    """
    Human-readable explanation for why the task got this score.
    """
    parts = []

    # urgency / due date
    due_date = task.get("due_date")
    if due_date:
        days_left = (due_date - date.today()).days
        if days_left < 0:
            parts.append("Overdue task")
        elif days_left == 0:
            parts.append("Due today")
        elif days_left <= 3:
            parts.append("Due soon (in {} day(s))".format(days_left))
        else:
            parts.append("Due later (in {} day(s))".format(days_left))
    else:
        parts.append("No strict deadline")

    # importance
    importance = task.get("importance", 5)
    parts.append("Importance: {}/10".format(importance))

    # effort
    est = task.get("estimated_hours")
    if est is not None:
        parts.append("Estimated effort: {} hour(s)".format(est))

    # dependencies
    dep_score = calculate_dependency_score(task.get("id"), all_tasks)
    if dep_score > 0:
        parts.append("Blocks other tasks")

    # cycles
    tid = task.get("id")
    if tid is not None and tid in cycles:
        parts.append("⚠ In a circular dependency – review dependencies")

    parts.append("Strategy: {}".format(strategy))

    return "; ".join(parts)
