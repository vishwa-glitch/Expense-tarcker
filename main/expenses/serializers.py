from rest_framework import serializers
from django.utils import timezone
from datetime import date
from decimal import Decimal
from django.utils.timezone import now
from .models import Expenses

class ExpenseSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Expenses
        fields = [
            'id',
            'amount',
            'category',
            'category_display',
            'description',
            'date',
            'payment_method',
            'payment_method_display',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("Start date cannot be later than end date.")

        return attrs

    def validate_amount(self, value):
        """
        Ensure that the amount is a positive value.
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive value.")
        return value
    
    def validate_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Expense date cannot be in the future")
        return value