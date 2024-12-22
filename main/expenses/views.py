from django.utils.timezone import now
from datetime import timedelta
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Expenses
from .serializers import Expenses_serializers
from rest_framework.permissions import IsAuthenticated

class ExpensesListView(viewsets.ModelViewSet):
    serializer_class = Expenses_serializers
    permission_classes = [IsAuthenticated]  
  
    def get_queryset(self):
        """
        Restrict the queryset to only the expenses of the authenticated user.
        """
        queryset = Expenses.objects.filter(user=self.request.user)  
        
        # Get filter parameters from the request
        filter_type = self.request.query_params.get('filter', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        # Filter by "Past week"
        if filter_type == 'past_week':
            one_week_ago = now() - timedelta(weeks=1)
            queryset = queryset.filter(date__gte=one_week_ago)

        # Filter by "Past month"
        elif filter_type == 'past_month':
            one_month_ago = now() - timedelta(days=30)
            queryset = queryset.filter(date__gte=one_month_ago)

        # Filter by "Last 3 months"
        elif filter_type == 'last_3_months':
            three_months_ago = now() - timedelta(days=90)
            queryset = queryset.filter(date__gte=three_months_ago)

        # Filter by custom date range
        elif filter_type == 'custom' and start_date and end_date:
            queryset = queryset.filter(date__gte=start_date, date__lte=end_date)

        return queryset
    
    def perform_create(self, serializer):
        """
        Automatically associate the authenticated user with the expense.
        """
        # The user is automatically assigned based on the authenticated user from the request
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        """
        Update the expense for the authenticated user only.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Ensure the expense belongs to the authenticated user
        if instance.user != request.user:
            return Response({"detail": "You do not have permission to edit this expense."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(serializer.data)
