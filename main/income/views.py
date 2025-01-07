from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta, timezone
from django.db.models import Sum, Avg
from .serializer import IncomeSerializer, IncomeAnalyticsSerializer, Income
from dateutil.relativedelta import relativedelta
from rest_framework.permissions import IsAuthenticated

class IncomeViewSet(viewsets.ModelViewSet):
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['income_type','recurring', 'date']
    search_fields = ['description']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        return Income.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        period = request.query_params.get('period', '12')  # months
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=int(period))
        
        summary = Income.get_income_summary(
            user=request.user,
            start_date=start_date,
            end_date=end_date
        )
        
        serializer = IncomeAnalyticsSerializer(summary, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        months = int(request.query_params.get('months', '12'))
        summary = Income.get_monthly_income(request.user, months=months)
        return Response(summary)

    @action(detail=False, methods=['get'])
    def recurring_income(self, request):
        queryset = self.get_queryset().filter(recurring=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)