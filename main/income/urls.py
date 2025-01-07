from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncomeViewSet
# Initialize a router
router = DefaultRouter()

# Register the ExpensesViewSet with the router
router.register(r'income', IncomeViewSet, basename='incomes')

urlpatterns = [
    path('', include(router.urls)),
]
