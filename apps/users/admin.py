from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model that uses email as the primary identifier
    """
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 
                    'subscription_status', 'is_on_trial')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'subscription_status', 'is_on_trial')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')}),
        (_('Subscription info'), {'fields': ('subscription_status', 'is_on_trial', 
                                             'trial_start_date', 'trial_end_date',
                                             'razorpay_customer_id')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
