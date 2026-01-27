from rest_framework import serializers

from app_todo.models import Todo



class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = (
            'TodoId',
            'UserId',
            'Title',
            'CreatedDate',
            'ScheduledOn',
            'IsCompleted'

        )