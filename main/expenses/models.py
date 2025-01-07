from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from dateutil.relativedelta import relativedelta

class Expenses(models.Model):
    # Payment Method Choices
    CASH = 'CASH'
    DEBIT_CARD = 'DEBIT_CARD'
    CREDIT_CARD = 'CREDIT_CARD'
    BANK_TRANSFER = 'BANK_TRANSFER'
    DIGITAL_WALLET = 'DIGITAL_WALLET'

    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Cash'),
        (DEBIT_CARD, 'Debit Card'),
        (CREDIT_CARD, 'Credit Card'),
        (BANK_TRANSFER, 'Bank Transfer'),
        (DIGITAL_WALLET, 'Digital Wallet'),
    ]

    # Expense Category Choices
    FOOD = 'FOOD'
    TRANSPORTATION = 'TRANSPORTATION'
    HOUSING = 'HOUSING'
    UTILITIES = 'UTILITIES'
    HEALTHCARE = 'HEALTHCARE'
    ENTERTAINMENT = 'ENTERTAINMENT'
    SHOPPING = 'SHOPPING'
    PERSONAL_CARE = 'PERSONAL_CARE'
    EDUCATION = 'EDUCATION'
    TRAVEL = 'TRAVEL'
    MISCELLANEOUS = 'MISCELLANEOUS'

    CATEGORY_CHOICES = [
        (FOOD, 'Food'),
        (TRANSPORTATION, 'Transportation'),
        (HOUSING, 'Housing'),
        (UTILITIES, 'Utilities'),
        (HEALTHCARE, 'Healthcare'),
        (ENTERTAINMENT, 'Entertainment'),
        (SHOPPING, 'Shopping'),
        (PERSONAL_CARE, 'Personal Care'),
        (EDUCATION, 'Education'),
        (TRAVEL, 'Travel'),
        (MISCELLANEOUS, 'Miscellaneous'),
    ]

    # Fields from TimeStampedModel
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Main model fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    category = models.CharField(
        choices=CATEGORY_CHOICES, 
        max_length=20,
        db_index=True
    )
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField(db_index=True)
    payment_method = models.CharField(
        choices=PAYMENT_METHOD_CHOICES, 
        max_length=20,
        db_index=True
    )

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
        ]
        verbose_name_plural = "Expenses"

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

    @classmethod
    def get_category_summary(cls, user, start_date, end_date):
        return cls.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).values('category').annotate(
            total=Sum('amount'),
            average=Avg('amount'),
            count=models.Count('id')
        ).order_by('-total')

    @classmethod
    def get_payment_method_summary(cls, user, start_date, end_date):
        return cls.objects.filter(
            user=user,
            date__range=[start_date, end_date]
        ).values('payment_method').annotate(
            total=Sum('amount'),
            count=models.Count('id')
        ).order_by('-total')

    @classmethod
    def get_monthly_comparison(cls, user, months=3):
        end_date = timezone.now().date()
        start_date = end_date - relativedelta(months=months)
        
        return cls.objects.filter(
            user=user,
            date__gte=start_date
        ).values('date__year', 'date__month').annotate(
            total=Sum('amount'),
            avg_transaction=Avg('amount'),
            transaction_count=models.Count('id')
        ).order_by('date__year', 'date__month')