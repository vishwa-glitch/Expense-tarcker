from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, F
from django.utils import timezone
from .models import Budget, BudgetCategory, BudgetNotification
from .serializer import (
    BudgetSerializer, BudgetCategorySerializer,
    BudgetNotificationSerializer
)

class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user).prefetch_related(
            'categories'
        ).annotate(
            total_spent=Sum('categories__expenses__amount'),
            remaining_budget=F('total_limit') - Sum('categories__expenses__amount')
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        budget = self.get_object()
        status_data = budget.get_budget_status()
        return Response(status_data)

    @action(detail=True, methods=['post'])
    def rollover(self, request, pk=None):
        budget = self.get_object()
        if not budget.rollover_enabled:
            return Response(
                {"detail": "Rollover not enabled for this budget"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new budget for next period
        new_start_date = budget.get_next_period_start_date()
        new_budget = Budget.objects.create(
            user=request.user,
            name=budget.name,
            period=budget.period,
            start_date=new_start_date,
            total_limit=budget.total_limit,
            rollover_enabled=budget.rollover_enabled
        )

        # Copy categories and adjust limits based on remaining amounts
        for category in budget.categories.all():
            status_data = category.get_status()
            new_limit = category.limit + status_data['remaining']
            BudgetCategory.objects.create(
                budget=new_budget,
                category=category.category,
                limit=new_limit,
                alert_threshold=category.alert_threshold,
                notification_enabled=category.notification_enabled
            )

        return Response(BudgetSerializer(new_budget).data)

class BudgetCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetCategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BudgetCategory.objects.filter(
            budget__user=self.request.user
        ).annotate(
            spent_amount=Sum('expenses__amount'),
            remaining_amount=F('limit') - Sum('expenses__amount'),
            percentage_used=Sum('expenses__amount') * 100.0 / F('limit')
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if 'budget_pk' in self.kwargs:
            context['budget'] = Budget.objects.get(
                pk=self.kwargs['budget_pk'],
                user=self.request.user
            )
        return context

    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        category = self.get_object()
        status_data = category.get_status()
        return Response(status_data)

class BudgetNotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BudgetNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BudgetNotification.objects.filter(
            budget_category__budget__user=self.request.user
        )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        self.get_queryset().update(read=True)
        return Response({'status': 'all notifications marked as read'})