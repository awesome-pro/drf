from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.common.models import Subscription, SubscriptionHistory
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    SubscriptionSerializer, 
    SubscriptionHistorySerializer,
    PasswordChangeSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Override to allow registration without authentication
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action
        """
        if self.action == 'create':
            return UserRegistrationSerializer
        return self.serializer_class
    
    def get_queryset(self):
        """
        Filter queryset to only show the current user unless staff
        """
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Endpoint to get current user's details
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """
        Endpoint to change user password
        """
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({"old_password": ["Wrong password."]}, 
                                status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"message": "Password updated successfully"}, 
                            status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def start_trial(self, request):
        """
        Endpoint to start a 30-day free trial
        """
        user = request.user
        
        # Check if user is already on trial or has an active subscription
        if user.is_on_trial:
            return Response(
                {"detail": "You are already on a trial period."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.subscription_status == 'active':
            return Response(
                {"detail": "You already have an active subscription."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Start the trial
        user.start_trial()
        
        # Create subscription history record
        subscription, created = Subscription.objects.get_or_create(user=user)
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='trial_started',
            new_plan='free',
            notes='30-day free trial started'
        )
        
        return Response(
            {"detail": "Your 30-day free trial has been started."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['post'])
    def cancel_subscription(self, request):
        """
        Endpoint to cancel subscription
        """
        user = request.user
        
        # Check if user has an active subscription or trial
        if user.subscription_status not in ['active', 'trial']:
            return Response(
                {"detail": "You don't have an active subscription to cancel."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the subscription
        user.cancel_subscription()
        
        # Create subscription history record
        subscription = Subscription.objects.get(user=user)
        previous_plan = subscription.plan
        
        SubscriptionHistory.objects.create(
            subscription=subscription,
            action='cancelled',
            previous_plan=previous_plan,
            notes='Subscription cancelled by user'
        )
        
        return Response(
            {"detail": "Your subscription has been cancelled."},
            status=status.HTTP_200_OK
        )


class RegistrationAPIView(generics.CreateAPIView):
    """
    API view for user registration with trial activation
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully. Your 30-day free trial has been activated.'
        }, status=status.HTTP_201_CREATED)


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing subscriptions
    """
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset to only show the current user's subscription unless staff
        """
        user = self.request.user
        if user.is_staff:
            return Subscription.objects.all()
        return Subscription.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """
        Set the user to the current user when creating
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_subscription(self, request):
        """
        Endpoint to get current user's subscription details
        """
        try:
            subscription = Subscription.objects.get(user=request.user)
            serializer = self.get_serializer(subscription)
            return Response(serializer.data)
        except Subscription.DoesNotExist:
            return Response(
                {"detail": "You don't have any subscription."},
                status=status.HTTP_404_NOT_FOUND
            )


class SubscriptionHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing subscription history
    """
    serializer_class = SubscriptionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter queryset to only show the current user's subscription history unless staff
        """
        user = self.request.user
        if user.is_staff:
            return SubscriptionHistory.objects.all()
        return SubscriptionHistory.objects.filter(subscription__user=user)


class CheckTrialStatusView(APIView):
    """
    API view to check trial status and expiration
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if not user.is_on_trial:
            return Response({
                "is_on_trial": False,
                "message": "You are not currently on a trial."
            })
        
        days_left = 0
        if user.trial_end_date:
            # Calculate days left in trial
            now = timezone.now()
            if user.trial_end_date > now:
                days_left = (user.trial_end_date - now).days
                
                # Add warning if trial is about to expire
                if days_left <= 3:
                    message = f"Your trial will expire in {days_left} days. Please subscribe to continue using our services."
                else:
                    message = f"You have {days_left} days left in your trial."
            else:
                # Trial has expired
                message = "Your trial has expired. Please subscribe to continue using our services."
                days_left = 0
        else:
            message = "Trial information is incomplete."
        
        return Response({
            "is_on_trial": user.is_on_trial,
            "trial_start_date": user.trial_start_date,
            "trial_end_date": user.trial_end_date,
            "days_left": days_left,
            "message": message
        })
