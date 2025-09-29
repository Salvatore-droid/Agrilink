from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from .models import SecuritySettings
from django.utils import timezone

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if user exists with username or email
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
            
            # Check security settings
            try:
                security_settings = user.security_settings
                if (security_settings.account_locked_until and 
                    security_settings.account_locked_until > timezone.now()):
                    return None
            except SecuritySettings.DoesNotExist:
                security_settings = SecuritySettings.objects.create(user=user)
            
            # Verify password
            if user.check_password(password):
                # Reset failed login attempts on successful login
                security_settings.failed_login_attempts = 0
                security_settings.account_locked_until = None
                security_settings.save()
                
                # Log login history
                self.log_login_history(user, request, True)
                return user
            else:
                # Increment failed login attempts
                security_settings.failed_login_attempts += 1
                if security_settings.failed_login_attempts >= 5:
                    security_settings.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
                security_settings.save()
                
                # Log failed attempt
                self.log_login_history(user, request, False)
                return None
                
        except User.DoesNotExist:
            return None
    
    def log_login_history(self, user, request, success):
        from .models import LoginHistory
        
        LoginHistory.objects.create(
            user=user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=success
        )
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip