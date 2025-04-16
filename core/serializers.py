from rest_framework import serializers
from .models import Columns, Boards, Cards

class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Columns
        fields = "__all__"


class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Boards
        fields = ['id', 'title', 'user']
        read_only_fields = ['user']

        def create(self, validated_data):
            # Assign the authenticated user automatically
            validated_data['user'] = self.context['request'].user
            return super().create(validated_data)


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = ['id', 'task', 'position', 'description', 'due_date', 'column', 'priority']
        read_only_fields = ['id', 'position', 'description', 'due_date']

class UpdateCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cards
        fields = ['id', 'task', 'position', 'description', 'due_date', 'column', 'priority']