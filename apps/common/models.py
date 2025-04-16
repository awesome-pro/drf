from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Subscription(TimeStampedModel):
    """
    Model to track subscription details for users
    """
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=50, choices=[
        ('free', 'Free'),
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ], default='free')
    
    # Razorpay specific fields
    razorpay_subscription_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Subscription status and dates
    is_active = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    
    # Payment information
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='INR')
    
    # Billing cycle
    billing_cycle = models.CharField(max_length=20, choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ], default='monthly')
    
    # Auto-renewal settings
    auto_renew = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.plan} ({self.get_billing_cycle_display()})"
    
    class Meta:
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')


class SubscriptionHistory(TimeStampedModel):
    """
    Model to track subscription history and changes
    """
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=50, choices=[
        ('created', 'Created'),
        ('renewed', 'Renewed'),
        ('upgraded', 'Upgraded'),
        ('downgraded', 'Downgraded'),
        ('cancelled', 'Cancelled'),
        ('trial_started', 'Trial Started'),
        ('trial_ended', 'Trial Ended'),
        ('payment_failed', 'Payment Failed'),
    ])
    
    # Previous and new values for tracking changes
    previous_plan = models.CharField(max_length=50, blank=True, null=True)
    new_plan = models.CharField(max_length=50, blank=True, null=True)
    
    # Payment information if applicable
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Additional notes
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.subscription.user.email} - {self.action} on {self.created_at}"
    
    class Meta:
        verbose_name = _('subscription history')
        verbose_name_plural = _('subscription histories')
        ordering = ['-created_at']
