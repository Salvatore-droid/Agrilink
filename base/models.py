from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinLengthValidator
import json

class UserProfile(models.Model):
    USER_TYPES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('both', 'Both'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPES)
    phone_number = models.CharField(max_length=15, validators=[MinLengthValidator(10)])
    location = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.user_type}"

class LoginHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Login Histories"
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    def __str__(self):
        return f"Password reset for {self.user.username}"

class SecuritySettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_settings')
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_method = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('sms', 'SMS')],
        default='email'
    )
    last_password_change = models.DateTimeField(auto_now_add=True)
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Security settings for {self.user.username}"

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-seedling')
    
    def __str__(self):
        return self.name

from django.db import models
from django.core.files.storage import FileSystemStorage
import os

# Optional: Custom storage for better organization
def product_image_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/products/user_<id>/<filename>
    return f'products/user_{instance.farmer.id}/{filename}'

class Product(models.Model):
    QUALITY_CHOICES = [
        ('premium', 'Premium'),
        ('grade1', 'Grade 1'),
        ('grade2', 'Grade 2'),
        ('standard', 'Standard'),
    ]
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)
    quality_grade = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='standard')
    location = models.CharField(max_length=100, null=True)
    harvest_date = models.DateField()
    is_available = models.BooleanField(default=True)
    
    # Replace image_url with actual ImageField
    image = models.ImageField(
        upload_to=product_image_path,  # Custom upload path
        null=True, 
        blank=True,
        verbose_name="Product Image"
    )
    
    # Keep image_url as backup or for external images
    image_url = models.CharField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} by {self.farmer.username}"
    
    # Optional: Property to get image URL with fallback
    @property
    def image_display(self):
        if self.image:
            return self.image.url
        elif self.image_url:
            return self.image_url
        return '/static/images/default-product.png'  # Add a default image

class PriceSuggestion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_suggestions')
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2)
    factors_considered = models.JSONField(default=dict)
    price_label = models.CharField(max_length=20, choices=[
        ('best_price', 'Best Price'),
        ('good_price', 'Good Price'),
        ('fair_price', 'Fair Price'),
        ('high_price', 'High Price')
    ], null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Suggested {self.suggested_price} for {self.product.name}"

class Order(models.Model):
    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.product.name}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']

class MarketTrend(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    average_price = models.DecimalField(max_digits=10, decimal_places=2)
    price_trend = models.CharField(max_length=10, choices=[
        ('increasing', 'Increasing'),
        ('decreasing', 'Decreasing'),
        ('stable', 'Stable')
    ])
    demand_level = models.CharField(max_length=10, choices=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low')
    ])
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.category.name} Market Trend"

class AIRecommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    recommended_products = models.ManyToManyField(Product)
    reason = models.TextField()
    confidence = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    query = models.CharField(max_length=255)
    results_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Testimonial by {self.user.username}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

# Add these models to your existing models.py

class PriceSuggestionRequest(models.Model):
    """Model for buyers to request/suggest prices for products"""
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='price_suggestions')
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    suggested_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_needed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=20, default='kg')
    location = models.CharField(max_length=100)
    urgency = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], default='medium')
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('expired', 'Expired')
    ], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.product_name} - {self.suggested_price} by {self.buyer.username}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class FarmerPriceResponse(models.Model):
    """Model for farmers to respond to price suggestions"""
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    price_suggestion = models.ForeignKey(PriceSuggestionRequest, on_delete=models.CASCADE, related_name='responses')
    counter_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('countered', 'Countered')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Response to {self.price_suggestion.product_name} by {self.farmer.username}"