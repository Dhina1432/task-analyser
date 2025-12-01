from rest_framework import serializers


class TaskInputSerializer(serializers.Serializer):
    """
    Used for /api/tasks/analyze/ input.
    """
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField(required=False, allow_null=True)
    estimated_hours = serializers.FloatField(required=False, allow_null=True)
    importance = serializers.IntegerField(min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
