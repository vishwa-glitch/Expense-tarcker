from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpensesViewSet

# Initialize a router
router = DefaultRouter()

# Register the ExpensesViewSet with the router
router.register(r'expenses', ExpensesViewSet, basename='expenses')

urlpatterns = [
    path('', include(router.urls)),
]
