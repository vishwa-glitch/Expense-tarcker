from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta


class Income(models.Model):
    # Income Type Choices
    SALARY = 'SALARY'
    FREELANCE = 'FREELANCE'
    BUSINESS = 'BUSINESS'
    INVESTMENTS = 'INVESTMENTS'
    RENTAL = 'RENTAL'
    DIVIDEND = 'DIVIDEND'
    INTEREST = 'INTEREST'
    BONUS = 'BONUS'
    OTHER = 'OTHER'

    INCOME_TYPE_CHOICES = [
        (SALARY, 'Salary'),
        (FREELANCE, 'Freelance'),
        (BUSINESS, 'Business'),
        (INVESTMENTS, 'Investment Income'),
        (RENTAL, 'Rental Income'),
        (DIVIDEND, 'Dividend'),
        (INTEREST, 'Interest'),
        (BONUS, 'Bonus'),
        (OTHER, 'Other'),
    ]

    # Frequency Choices
    FREQUENCY_CHOICES = [
        ('ONE_TIME', 'One-Time'),
        ('DAILY', 'Daily'),
        ('WEEKLY', 'Weekly'),
        ('BIWEEKLY', 'Bi-weekly'),
        ('MONTHLY', 'Monthly'),
        ('QUARTERLY', 'Quarterly'),
        ('BIANNUALLY', 'Bi-annually'),
        ('ANNUALLY', 'Annually'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('JPY', 'Japanese Yen'),
        ('AUD', 'Australian Dollar'),
        ('CAD', 'Canadian Dollar'),
        ('INR', 'Indian Rupee'),
        ('CNY', 'Chinese Yuan'),
        ('CHF', 'Swiss Franc'),
        ('SGD', 'Singapore Dollar'),
        ('NZD', 'New Zealand Dollar'),
        ('HKD', 'Hong Kong Dollar'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    income_type = models.CharField(
        choices=INCOME_TYPE_CHOICES,
        max_length=20,
        db_index=True
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD'
    )
    date = models.DateField(db_index=True)
    description = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Source of income (e.g., employer name, client name)"
    )
    recurring = models.BooleanField(
        default=False,
        help_text="Whether this income occurs regularly"
    )
    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        null=True,
        blank=True,
        help_text="Frequency of recurring income"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'income_type']),
            models.Index(fields=['user', 'recurring']),
            models.Index(fields=['user', 'currency']),
        ]
        verbose_name_plural = "Incomes"
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount__gt=0),
                name='income_amount_positive'
            )
        ]

    def __str__(self):
        return f"{self.income_type} - {self.amount} on {self.date}"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.recurring and not self.frequency:
            raise ValidationError({
                'frequency': 'Frequency is required for recurring income'
            })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_income_summary(cls, user, start_date, end_date):
        """Get summary of income by type for a date range"""
        return cls.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).values('income_type').annotate(
            total=Sum('amount'),
            average=Avg('amount'),
            count=models.Count('id')
        ).order_by('-total')

    @classmethod
    def get_monthly_income(cls, user, months=12):
        """Get monthly income totals for the last specified months"""
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=months)
        
        return cls.objects.filter(
            user=user,
            date__gte=start_date
        ).values('date__year', 'date__month').annotate(
            total=Sum('amount'),
            unique_sources=models.Count('income_type', distinct=True),
            regular_income=Sum('amount', filter=models.Q(recurring=True)),
            one_time_income=Sum('amount', filter=models.Q(recurring=False))
        ).order_by('date__year', 'date__month')

    @property
    def next_expected_date(self):
        """Calculate next expected date for recurring income"""
        if not self.recurring or not self.frequency:
            return None
            
        if self.frequency == 'MONTHLY':
            return self.date + relativedelta(months=1)
        elif self.frequency == 'WEEKLY':
            return self.date + relativedelta(weeks=1)
        elif self.frequency == 'BIWEEKLY':
            return self.date + relativedelta(weeks=2)
        elif self.frequency == 'QUARTERLY':
            return self.date + relativedelta(months=3)
        elif self.frequency == 'ANNUALLY':
            return self.date + relativedelta(years=1)
        return None