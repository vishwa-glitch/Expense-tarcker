from django.db import models
from django.contrib.auth.models import User

class Expenses(models.Model):
    CATEGORY_CHOICES = [
        ('FOOD', 'Food'),
        ('TRANSPORTATION', 'Transportation'),
        ('HOUSING', 'Housing'),
        ('UTILITIES', 'Utilities'),
        ('HEALTHCARE', 'Healthcare'),
        ('ENTERTAINMENT', 'Entertainment'),
        ('SHOPPING', 'Shopping'),
        ('PERSONAL_CARE', 'Personal Care'),
        ('EDUCATION', 'Education'),
        ('TRAVEL', 'Travel'),
        ('MISCELLANEOUS', 'Miscellaneous'),
    ]
    PAYMENT_CHOICES = [
        ('CASH', 'Cash'),
        ('DEBIT CARD', 'Debit '),
        ('CREDIT CARD', 'Credit Card'),
        ('BANK TRANSFER', 'Bank Transfer'),
        ('DIGITAL WALLET', 'Digital Wallet'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20)
    description = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    payment_methods = models.CharField(choices=PAYMENT_CHOICES, max_length=20)