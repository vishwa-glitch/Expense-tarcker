from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from expenses.models import Expenses
class Budget(models.Model):
    PERIOD_CHOICES = [
        ('WEEKLY', 'Weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('ANNUALLY', 'Annually'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    name = models.CharField(max_length=100)
    period = models.CharField(
        max_length=20,
        choices=PERIOD_CHOICES,
        default='MONTHLY'
    )
    start_date = models.DateField()
    total_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total budget limit for the period"
    )
    rollover_enabled = models.BooleanField(
        default=False,
        help_text="Enable rolling over unused budget to next period"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date', 'name']
        indexes = [
            models.Index(fields=['user', 'start_date']),
            models.Index(fields=['user', 'period']),
        ]

    def __str__(self):
        return f"{self.name} - {self.period} ({self.start_date})"

    def get_end_date(self):
        if self.period == 'WEEKLY':
            return self.start_date + relativedelta(weeks=1)
        elif self.period == 'MONTHLY':
            return self.start_date + relativedelta(months=1)
        elif self.period == 'QUARTERLY':
            return self.start_date + relativedelta(months=3)
        else:  # ANNUALLY
            return self.start_date + relativedelta(years=1)

    def get_next_period_start_date(self):
        return self.get_end_date()

    def get_budget_status(self):
        """Calculate current budget status including spending and remaining amounts"""
        end_date = self.get_end_date()
        total_spent = self.categories.aggregate(
            spent=models.Sum('expenses__amount')
        )['spent'] or Decimal('0')
        
        remaining = self.total_limit - total_spent
        percentage_used = (total_spent / self.total_limit * 100) if total_spent > 0 else 0
        
        return {
            'total_limit': self.total_limit,
            'total_spent': total_spent,
            'remaining': remaining,
            'percentage_used': percentage_used
        }

class BudgetCategory(models.Model):
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='categories'
    )
    category = models.CharField(
        max_length=20,
        choices=Expenses.CATEGORY_CHOICES,
        db_index=True
    )
    limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    alert_threshold = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=80.00,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Percentage at which to trigger an alert"
    )
    notification_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['budget', 'category']
        ordering = ['category']

    def __str__(self):
        return f"{self.get_category_display()} - {self.limit}"

    def clean(self):
        if self.limit > self.budget.total_limit:
            raise ValidationError({
                'limit': 'Category limit cannot exceed total budget limit'
            })

    def get_status(self):
        """Calculate current category status including spending and alerts"""
        end_date = self.budget.get_end_date()
        total_spent = Expenses.objects.filter(
            user=self.budget.user,
            category=self.category,
            date__range=[self.budget.start_date, end_date]
        ).aggregate(spent=models.Sum('amount'))['spent'] or Decimal('0')
        
        remaining = self.limit - total_spent
        percentage_used = (total_spent / self.limit * 100) if total_spent > 0 else 0
        alert_triggered = percentage_used >= self.alert_threshold
        
        return {
            'limit': self.limit,
            'spent': total_spent,
            'remaining': remaining,
            'percentage_used': percentage_used,
            'alert_triggered': alert_triggered
        }

class BudgetNotification(models.Model):
    THRESHOLD_REACHED = 'THRESHOLD_REACHED'
    LIMIT_EXCEEDED = 'LIMIT_EXCEEDED'
    BUDGET_RESET = 'BUDGET_RESET'
    
    NOTIFICATION_TYPE_CHOICES = [
        (THRESHOLD_REACHED, 'Threshold Reached'),
        (LIMIT_EXCEEDED, 'Limit Exceeded'),
        (BUDGET_RESET, 'Budget Reset'),
    ]

    budget_category = models.ForeignKey(
        BudgetCategory,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPE_CHOICES
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['budget_category', 'created_at']),
            models.Index(fields=['budget_category', 'read']),
        ]

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.created_at}"