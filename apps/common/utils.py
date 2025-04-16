import razorpay
from django.conf import settings
from django.utils import timezone
import datetime
import logging

logger = logging.getLogger(__name__)


class RazorpayClient:
    """
    Utility class to handle Razorpay API operations
    """
    def __init__(self):
        self.key_id = settings.RAZORPAY_KEY_ID
        self.key_secret = settings.RAZORPAY_KEY_SECRET
        self.client = None
        
        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
    
    def create_customer(self, name, email, contact=None):
        """
        Create a customer in Razorpay
        """
        if not self.client:
            logger.warning("Razorpay client not initialized. Check your API keys.")
            return None
        
        try:
            customer_data = {
                'name': name,
                'email': email,
            }
            
            if contact:
                customer_data['contact'] = contact
                
            customer = self.client.customer.create(data=customer_data)
            return customer
        except Exception as e:
            logger.error(f"Error creating Razorpay customer: {str(e)}")
            return None
    
    def create_subscription(self, plan_id, customer_id, total_count=None, start_at=None):
        """
        Create a subscription in Razorpay
        If total_count is not provided, it will be an infinite subscription
        If start_at is not provided, it will start immediately after authorization
        """
        if not self.client:
            logger.warning("Razorpay client not initialized. Check your API keys.")
            return None
        
        try:
            subscription_data = {
                'plan_id': plan_id,
                'customer_notify': 1,  # Notify the customer
                'customer_id': customer_id,
            }
            
            # Add total_count if provided (for limited period subscriptions)
            if total_count:
                subscription_data['total_count'] = total_count
            
            # Add start_at if provided (for delayed start)
            if start_at:
                # Convert to Unix timestamp
                if isinstance(start_at, datetime.datetime):
                    start_at = int(start_at.timestamp())
                subscription_data['start_at'] = start_at
            
            subscription = self.client.subscription.create(data=subscription_data)
            return subscription
        except Exception as e:
            logger.error(f"Error creating Razorpay subscription: {str(e)}")
            return None
    
    def cancel_subscription(self, subscription_id, cancel_at_cycle_end=True):
        """
        Cancel a subscription in Razorpay
        If cancel_at_cycle_end is True, it will be cancelled at the end of the current billing cycle
        Otherwise, it will be cancelled immediately
        """
        if not self.client:
            logger.warning("Razorpay client not initialized. Check your API keys.")
            return None
        
        try:
            return self.client.subscription.cancel(subscription_id, cancel_at_cycle_end)
        except Exception as e:
            logger.error(f"Error cancelling Razorpay subscription: {str(e)}")
            return None
    
    def create_plan(self, name, period, amount, currency='INR', description=None):
        """
        Create a plan in Razorpay
        period can be 'daily', 'weekly', 'monthly', 'yearly'
        amount is in the smallest currency unit (paise for INR)
        """
        if not self.client:
            logger.warning("Razorpay client not initialized. Check your API keys.")
            return None
        
        try:
            # First create an item
            item_data = {
                'name': name,
                'amount': amount,
                'currency': currency,
                'description': description or f"{name} Plan"
            }
            item = self.client.item.create(data=item_data)
            
            # Then create a plan with the item
            plan_data = {
                'period': period,
                'interval': 1,  # Every 1 period
                'item': {
                    'id': item['id'],
                    'name': item['name'],
                    'amount': item['amount'],
                    'currency': item['currency'],
                    'description': item['description']
                },
                'notes': {
                    'description': description or f"{name} Plan"
                }
            }
            
            plan = self.client.plan.create(data=plan_data)
            return plan
        except Exception as e:
            logger.error(f"Error creating Razorpay plan: {str(e)}")
            return None
    
    def get_subscription(self, subscription_id):
        """
        Get subscription details from Razorpay
        """
        if not self.client:
            logger.warning("Razorpay client not initialized. Check your API keys.")
            return None
        
        try:
            return self.client.subscription.fetch(subscription_id)
        except Exception as e:
            logger.error(f"Error fetching Razorpay subscription: {str(e)}")
            return None


def calculate_trial_end_date(start_date=None, days=30):
    """
    Calculate the end date for a trial period
    If start_date is not provided, current time is used
    """
    if start_date is None:
        start_date = timezone.now()
    
    return start_date + datetime.timedelta(days=days)


def is_trial_expiring_soon(trial_end_date, threshold_days=3):
    """
    Check if a trial is expiring soon (within threshold_days)
    """
    if not trial_end_date:
        return False
    
    now = timezone.now()
    time_left = trial_end_date - now
    
    # Check if trial has already expired
    if time_left.total_seconds() <= 0:
        return False
    
    # Check if trial is expiring within threshold_days
    return time_left.days <= threshold_days


def can_cancel_trial(trial_end_date):
    """
    Check if a trial can be cancelled (more than 24 hours before expiry)
    """
    if not trial_end_date:
        return False
    
    now = timezone.now()
    time_left = trial_end_date - now
    
    # Check if there's more than 24 hours left
    return time_left.total_seconds() > 24 * 60 * 60
