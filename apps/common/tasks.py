from celery import shared_task
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.common.models import Subscription, SubscriptionHistory

User = get_user_model()


@shared_task
def check_trial_expirations():
    """
    Background task to check for expired trials and update user statuses.
    This task should be scheduled to run daily.
    """
    now = timezone.now()
    
    # Find users with active trials that have expired
    expired_trials = User.objects.filter(
        is_on_trial=True,
        trial_end_date__lt=now,
        subscription_status='trial'
    )
    
    # Update each user's status
    for user in expired_trials:
        # Update user status
        user.is_on_trial = False
        user.subscription_status = 'expired'
        user.save()
        
        # Update subscription history
        try:
            subscription = Subscription.objects.get(user=user)
            
            # Create history record
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='trial_ended',
                previous_plan='free',
                notes='Trial period expired'
            )
            
        except Subscription.DoesNotExist:
            # If no subscription exists, create one in expired state
            subscription = Subscription.objects.create(
                user=user,
                plan='free',
                is_active=False
            )
            
            # Create history record
            SubscriptionHistory.objects.create(
                subscription=subscription,
                action='trial_ended',
                previous_plan='free',
                notes='Trial period expired without subscription record'
            )
    
    return f"Processed {expired_trials.count()} expired trials"


@shared_task
def send_trial_expiration_reminders():
    """
    Background task to send reminders to users whose trials are about to expire.
    Sends reminders 3 days, 1 day, and 12 hours before expiration.
    """
    now = timezone.now()
    
    # 3 days before expiration
    three_days_from_now = now + timezone.timedelta(days=3)
    users_3days = User.objects.filter(
        is_on_trial=True,
        trial_end_date__range=(now, three_days_from_now),
        subscription_status='trial'
    )
    
    # 1 day before expiration
    one_day_from_now = now + timezone.timedelta(days=1)
    users_1day = User.objects.filter(
        is_on_trial=True,
        trial_end_date__range=(now, one_day_from_now),
        subscription_status='trial'
    )
    
    # 12 hours before expiration
    twelve_hours_from_now = now + timezone.timedelta(hours=12)
    users_12hrs = User.objects.filter(
        is_on_trial=True,
        trial_end_date__range=(now, twelve_hours_from_now),
        subscription_status='trial'
    )
    
    # Here you would send emails or notifications to these users
    # For now, we'll just return the counts
    return {
        "3_days_reminder": users_3days.count(),
        "1_day_reminder": users_1day.count(),
        "12_hours_reminder": users_12hrs.count()
    }
