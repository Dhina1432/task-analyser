
from datetime import date, timedelta

from django.test import TestCase

from .scoring import score_task, detect_cycles


class ScoringTests(TestCase):
    def setUp(self):
        today = date.today()
        self.tasks = [
            {
                "id": 1,
                "title": "Important urgent task",
                "due_date": today - timedelta(days=1),  # overdue
                "estimated_hours": 2,
                "importance": 9,
                "dependencies": [],
            },
            {
                "id": 2,
                "title": "Less important future task",
                "due_date": today + timedelta(days=7),
                "estimated_hours": 2,
                "importance": 3,
                "dependencies": [],
            },
        ]

    def test_overdue_has_higher_score_than_future(self):
        score_overdue = score_task(self.tasks[0], self.tasks, strategy="deadline_driven")
        score_future = score_task(self.tasks[1], self.tasks, strategy="deadline_driven")
        self.assertGreater(
            score_overdue,
            score_future,
            msg="Overdue task should score higher than future task in deadline_driven strategy.",
        )

    def test_high_importance_has_higher_score_than_low(self):
        high = {
            "id": 3,
            "title": "High importance",
            "due_date": None,
            "estimated_hours": 2,
            "importance": 9,
            "dependencies": [],
        }
        low = {
            "id": 4,
            "title": "Low importance",
            "due_date": None,
            "estimated_hours": 2,
            "importance": 2,
            "dependencies": [],
        }
        all_tasks = [high, low]
        score_high = score_task(high, all_tasks, strategy="high_impact")
        score_low = score_task(low, all_tasks, strategy="high_impact")
        self.assertGreater(
            score_high,
            score_low,
            msg="High importance task should score higher in high_impact strategy.",
        )

    def test_detect_cycles_finds_circular_dependency(self):
        tasks = [
            {"id": 1, "dependencies": [2]},
            {"id": 2, "dependencies": [1]},
        ]
        cycles = detect_cycles(tasks)
        self.assertIn(1, cycles)
        self.assertIn(2, cycles)
