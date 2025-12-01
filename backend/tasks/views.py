from datetime import date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import TaskInputSerializer
from .scoring import score_task, detect_cycles, build_explanation
from .models import Task


class AnalyzeTasksView(APIView):
    """
    POST /api/tasks/analyze/

    Accepts: list of tasks (JSON)
    Returns: same tasks + score + explanation, sorted by score desc
    """

    def post(self, request):
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"error": "Expected a JSON array of tasks"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskInputSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)

        tasks = list(serializer.validated_data)

        # detect circular dependencies
        cycles = detect_cycles(tasks)

        strategy = request.query_params.get("strategy", "smart_balance")

        enriched = []
        for task in tasks:
            task_dict = dict(task)
            task_dict["score"] = score_task(task_dict, tasks, strategy=strategy)
            task_dict["explanation"] = build_explanation(
                task_dict, tasks, strategy, cycles
            )
            enriched.append(task_dict)

        # sort by score (highest first)
        enriched.sort(key=lambda t: t["score"], reverse=True)

        return Response(enriched, status=status.HTTP_200_OK)


class SuggestTasksView(APIView):
    """
    GET /api/tasks/suggest/

    Uses tasks stored in the database (Task model),
    scores them, and returns the top 3 with explanations.
    """

    def get(self, request):
        # Optionally, you could filter here, e.g. only tasks not done yet.
        qs = Task.objects.all()

        if not qs.exists():
            return Response(
                {"message": "No tasks found in the database. Add some tasks via admin or shell."},
                status=status.HTTP_200_OK,
            )

        # Convert queryset to list[dict] compatible with scoring functions
        tasks_data = []
        for t in qs:
            tasks_data.append({
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date,
                "estimated_hours": t.estimated_hours,
                "importance": t.importance,
                "dependencies": list(
                    t.dependencies.values_list("id", flat=True)
                ),
            })

        cycles = detect_cycles(tasks_data)
        strategy = request.query_params.get("strategy", "smart_balance")

        # compute scores + explanations
        for task in tasks_data:
            task["score"] = score_task(task, tasks_data, strategy=strategy)
            task["explanation"] = build_explanation(
                task, tasks_data, strategy, cycles
            )

        # sort and take top 3
        tasks_data.sort(key=lambda t: t["score"], reverse=True)
        top_three = tasks_data[:3]

        # Optionally annotate with "today" context
        today_str = date.today().isoformat()

        return Response(
            {
                "date": today_str,
                "strategy": strategy,
                "tasks": top_three,
            },
            status=status.HTTP_200_OK,
        )
