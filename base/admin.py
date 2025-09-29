from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, LoginHistory, SecuritySettings, PasswordResetToken

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class SecuritySettingsInline(admin.StackedInline):
    model = SecuritySettings
    can_delete = False
    verbose_name_plural = 'Security Settings'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, SecuritySettingsInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_user_type', 'is_staff')
    list_filter = ('profile__user_type', 'is_staff', 'is_superuser', 'is_active')
    
    def get_user_type(self, obj):
        return obj.profile.user_type
    get_user_type.short_description = 'User Type'

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'login_time', 'success')
    list_filter = ('success', 'login_time')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'login_time', 'success')

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at', 'is_used')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('user', 'token', 'created_at', 'expires_at')

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)