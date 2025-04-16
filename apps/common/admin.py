from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Subscription, SubscriptionHistory


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Subscription model
    """
    list_display = ('user', 'plan', 'is_active', 'start_date', 'end_date', 'billing_cycle')
    list_filter = ('plan', 'is_active', 'billing_cycle', 'auto_renew')
    search_fields = ('user__email', 'user__username', 'razorpay_subscription_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (None, {'fields': ('user', 'plan', 'is_active')}),
        (_('Dates'), {'fields': ('start_date', 'end_date', 'created_at', 'updated_at')}),
        (_('Billing'), {'fields': ('amount', 'currency', 'billing_cycle', 'auto_renew')}),
        (_('Razorpay'), {'fields': ('razorpay_subscription_id', 'razorpay_payment_id')}),
    )


@admin.register(SubscriptionHistory)
class SubscriptionHistoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for SubscriptionHistory model
    """
    list_display = ('subscription', 'action', 'created_at', 'previous_plan', 'new_plan')
    list_filter = ('action', 'created_at')
    search_fields = ('subscription__user__email', 'payment_id', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {'fields': ('subscription', 'action')}),
        (_('Plan Changes'), {'fields': ('previous_plan', 'new_plan')}),
        (_('Payment'), {'fields': ('payment_id', 'amount')}),
        (_('Additional Information'), {'fields': ('notes', 'created_at', 'updated_at')}),
    )
