from rest_framework import serializers
from .models import Trigger

class TriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trigger
        fields = ['id', 'user', 'value', 'status']
        read_only_fields = ['user']
