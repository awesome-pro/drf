from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.common.models import Subscription, SubscriptionHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                  'phone_number', 'profile_picture', 'subscription_status',
                  'is_on_trial', 'trial_start_date', 'trial_end_date')
        read_only_fields = ('id', 'is_on_trial', 'trial_start_date', 
                            'trial_end_date', 'subscription_status')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation"""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 
                  'phone_number', 'password', 'password_confirm')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # Remove password_confirm as it's not needed for creating the user
        validated_data.pop('password_confirm', None)
        
        # Create the user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        
        # Add additional fields if provided
        if 'phone_number' in validated_data:
            user.phone_number = validated_data['phone_number']
            user.save()
        
        # Start the trial for the new user
        user.start_trial()
        
        return user


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for the Subscription model"""
    
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Subscription
        fields = ('id', 'user', 'user_email', 'plan', 'is_active', 
                  'start_date', 'end_date', 'amount', 'currency', 
                  'billing_cycle', 'auto_renew', 'razorpay_subscription_id')
        read_only_fields = ('id', 'user', 'user_email', 'razorpay_subscription_id')
    
    def get_user_email(self, obj):
        return obj.user.email


class SubscriptionHistorySerializer(serializers.ModelSerializer):
    """Serializer for the SubscriptionHistory model"""
    
    subscription_id = serializers.PrimaryKeyRelatedField(source='subscription', read_only=True)
    user_email = serializers.SerializerMethodField()
    
    class Meta:
        model = SubscriptionHistory
        fields = ('id', 'subscription_id', 'user_email', 'action', 
                  'previous_plan', 'new_plan', 'payment_id', 
                  'amount', 'notes', 'created_at')
        read_only_fields = ('id', 'subscription_id', 'user_email', 'created_at')
    
    def get_user_email(self, obj):
        return obj.subscription.user.email


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change endpoint"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs
