from rest_framework import serializers
from .models import Expenses
from django.utils.timezone import now

class Expenses_serializers(serializers.ModelSerializer):
    description = serializers.CharField(max_length=255, required = False)

    class Meta:
        model = Expenses
        fields = [
        "id",
        'category',
        'amount',
        'date',
        'description',
        'payment_methods',
        ]


    def validate_amount(self, value):
      """Ensure that the amount is not negative"""
      if value <= 0:
          raise serializers.ValidationError("The amount cannot be negative or zero.")
      return value
    
    def validate_date(self, value):
        """Ensure the date is not in the future."""
        if value > now().date():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value
        
    def validate(self, data):
      if not data.get('category'):
          raise serializers.ValidationError("Category is required.")
      if not data.get('payment_methods'):
          raise serializers.ValidationError("Payment method is required.")
      return data
    
    def create(self, validated_data):
        # Automatically associate the authenticated user with the expense
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Automatically associate the authenticated user with the expense
        validated_data['user'] = self.context['request'].user
        return super().update(instance, validated_data)
