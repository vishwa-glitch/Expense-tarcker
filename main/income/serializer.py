from rest_framework import serializers
from .models import Income

class IncomeSerializer(serializers.ModelSerializer):
    net_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Income
        fields = [
            'id', 'amount', 'income_type', 'description', 'date',
            'source', 'recurring', 'frequency'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        if data.get('recurring'):
            if not data.get('frequency'):
                raise serializers.ValidationError(
                    "Frequency is required for recurring income"
                )
        return data

class IncomeAnalyticsSerializer(serializers.Serializer):
    income_type = serializers.CharField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
    average = serializers.DecimalField(max_digits=10, decimal_places=2)
    count = serializers.IntegerField()