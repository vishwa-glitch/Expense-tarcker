from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Avg
from dateutil.relativedelta import relativedelta
import calendar
from .serializers import ExpenseSerializer
from .models import Expenses
from django.db import models
from django.core.exceptions import ValidationError
from django.db import IntegrityError

class ExpensesViewSet(viewsets.ModelViewSet):
    
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category', 'payment_method', 'date']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'category']
    ordering = ['-date']

    def get_queryset(self):
        return Expenses.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        expense = serializer.save(user=self.request.user)
        return Response(ExpenseSerializer(expense).data)

    @action(detail=False, methods=['get'])
    def category_summary(self, request):

        start_date = request.query_params.get('start_date', 
            (timezone.now().date() - relativedelta(months=1)).isoformat())
        
        end_date = request.query_params.get('end_date', 
            timezone.now().date().isoformat())
        
        try:
            start_date = timezone.datetime.fromisoformat(start_date)
            end_date = timezone.datetime.fromisoformat(end_date)

        except ValueError:
            raise ValidationError("Invalid date format. Ensure dates are in ISO format (YYYY-MM-DD).")

        if start_date > end_date:
            raise ValidationError("Start date cannot be later than end date.")
        
        summary = Expenses.get_category_summary(
            self.request.user, 
            start_date, 
            end_date
        )
        return Response(summary)

    @action(detail=False, methods=['get'])
    def payment_method_summary(self, request):

        start_date = request.query_params.get('start_date', 
            (timezone.now().date() - relativedelta(months=1)).isoformat())
        
        end_date = request.query_params.get('end_date', 
            timezone.now().date().isoformat())
        
        try:
            start_date = timezone.datetime.fromisoformat(start_date)
            end_date = timezone.datetime.fromisoformat(end_date)

        except ValueError:
            raise ValidationError("Invalid date format. Ensure dates are in ISO format (YYYY-MM-DD).")

        if start_date > end_date:
            raise ValidationError("Start date cannot be later than end date.")
        
        summary = Expenses.get_payment_method_summary(
            self.request.user, 
            start_date, 
            end_date
        )
        return Response(summary)

    @action(detail=False, methods=['get'])
    def monthly_comparison(self, request):
        months = int(request.query_params.get('months', 3))
        comparison = Expenses.get_monthly_comparison(
            self.request.user, 
            months=months
        )
        return Response(comparison)

    @action(detail=False, methods=['get'])
    def trends(self, request):
        # Validate 'months' query parameter
        months_param = request.query_params.get('months', 6)  # Default to 6 months
        try:
            months = int(months_param)
            if months <= 0 or months > 12:
                raise ValueError("Months should be between 1 and 12.")
        except ValueError:
            raise ValidationError("Invalid 'months' parameter. It must be an integer between 1 and 12.")

        # Calculate date range
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=months)

        # Filter expenses
        expenses = self.get_queryset().filter(
            date__gte=start_date,
            date__lte=end_date
        )

        # Validate if any expenses exist
        if not expenses.exists():
            raise ValidationError(f"No expenses found for the selected period: {start_date} to {end_date}.")

        # Generate trends
        trends = {
            'total_spent': expenses.aggregate(total=Sum('amount'))['total'] or 0,
            'average_monthly': expenses.values('date__year', 'date__month')
                .annotate(total=Sum('amount'))
                .aggregate(avg=Avg('total'))['avg'] or 0,
            'highest_category': expenses.values('category')
                .annotate(total=Sum('amount'))
                .order_by('-total').first(),
            'most_used_payment': expenses.values('payment_method')
                .annotate(count=models.Count('id'))
                .order_by('-count').first(),
            'largest_expense': expenses.order_by('-amount').values(
                'amount', 'category', 'date', 'description'
            ).first(),
        }

        return Response(trends)
