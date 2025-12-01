from django.db import models

# Create your models here.
from django.db import models


class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateField(null=True, blank=True)
    estimated_hours = models.FloatField(null=True, blank=True)
    importance = models.IntegerField(default=5)  # 1–10 scale

    # Tasks that this task depends on (i.e., must be done BEFORE this one)
    dependencies = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='blocked_tasks'
    )

    def __str__(self):
        return self.title
