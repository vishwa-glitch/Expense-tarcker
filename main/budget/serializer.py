from rest_framework import serializers
from .models import Budget, BudgetCategory, BudgetNotification
from django.db.models import Sum
from decimal import Decimal

class BudgetCategorySerializer(serializers.ModelSerializer):
    spent_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    remaining_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    percentage_used = serializers.FloatField(read_only=True)
    
    class Meta:
        model = BudgetCategory
        fields = [
            'id', 'category', 'limit', 'alert_threshold', 
            'notification_enabled', 'spent_amount', 
            'remaining_amount', 'percentage_used'
        ]
        read_only_fields = ['id']

    def validate_limit(self, value):
        budget = self.context['budget']
        if value > budget.total_limit:
            raise serializers.ValidationError(
                "Category limit cannot exceed total budget limit"
            )
        return value

class BudgetSerializer(serializers.ModelSerializer):
    categories = BudgetCategorySerializer(many=True, read_only=True)
    total_spent = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    remaining_budget = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'period', 'start_date', 'total_limit',
            'rollover_enabled', 'categories', 'total_spent',
            'remaining_budget', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure total_limit is greater than sum of existing category limits
        if self.instance:  # For updates
            category_sum = self.instance.categories.aggregate(
                total=Sum('limit'))['total'] or Decimal('0')
            if data.get('total_limit', self.instance.total_limit) < category_sum:
                raise serializers.ValidationError(
                    "Total budget limit cannot be less than sum of category limits"
                )
        return data

class BudgetNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetNotification
        fields = [
            'id', 'budget_category', 'notification_type',
            'message', 'created_at', 'read'
        ]
        read_only_fields = ['id', 'created_at']