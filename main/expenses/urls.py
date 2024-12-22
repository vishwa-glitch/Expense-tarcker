from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpensesListView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Initialize a router
router = DefaultRouter()

# Register the ExpensesViewSet with the router
router.register(r'expenses', ExpensesListView, basename='expenses')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
