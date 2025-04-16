from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model that extends Django's AbstractUser.
    This allows for easy extension of the user model with additional fields.
    """
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(_('phone number'), max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    
    # Fields for subscription and trial management
    is_on_trial = models.BooleanField(default=False)
    trial_start_date = models.DateTimeField(null=True, blank=True)
    trial_end_date = models.DateTimeField(null=True, blank=True)
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('inactive', 'Inactive'),
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('cancelled', 'Cancelled'),
            ('expired', 'Expired'),
        ],
        default='inactive'
    )
    razorpay_customer_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Username still required by Django
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email
    
    def start_trial(self):
        """Start the 30-day free trial for this user"""
        from django.utils import timezone
        import datetime
        
        self.is_on_trial = True
        self.trial_start_date = timezone.now()
        self.trial_end_date = self.trial_start_date + datetime.timedelta(days=30)
        self.subscription_status = 'trial'
        self.save()
    
    def cancel_subscription(self):
        """Cancel the user's subscription"""
        self.subscription_status = 'cancelled'
        self.save()
    
    def is_trial_expired(self):
        """Check if the user's trial has expired"""
        from django.utils import timezone
        
        if not self.is_on_trial:
            return False
        
        return self.trial_end_date and self.trial_end_date < timezone.now()
