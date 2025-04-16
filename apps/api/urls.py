from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    UserViewSet, 
    RegistrationAPIView, 
    SubscriptionViewSet, 
    SubscriptionHistoryViewSet,
    CheckTrialStatusView
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
router.register(r'subscription-history', SubscriptionHistoryViewSet, basename='subscription-history')

# URL patterns for our API
urlpatterns = [
    # Include the router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('auth/register/', RegistrationAPIView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Subscription-related endpoints
    path('trial/status/', CheckTrialStatusView.as_view(), name='trial-status'),
]
