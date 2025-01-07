from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'categories', views.BudgetCategoryViewSet, basename='budgetcategory')
router.register(r'notifications', views.BudgetNotificationViewSet, basename='budgetnotification')

urlpatterns = [
    path('', include(router.urls)),
]