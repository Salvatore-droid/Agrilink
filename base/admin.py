from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *

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
    list_display = ('user', 'created_at', 'expires_at', 'is_used', 'is_valid')
    list_filter = ('is_used', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('user', 'token', 'created_at', 'expires_at')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)
    list_editable = ('icon',)

from django.utils.html import format_html

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'farmer', 'category', 'price', 'quantity', 'unit', 'quality_grade', 'is_available', 'image_preview', 'created_at')
    list_filter = ('category', 'quality_grade', 'is_available', 'created_at')
    search_fields = ('name', 'farmer__username', 'location')
    list_editable = ('price', 'quantity', 'is_available')
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    
    # Add image preview in list view
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        elif obj.image_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image_url)
        return "No Image"
    image_preview.short_description = 'Image Preview'
    
    # Custom form for better image upload
    fieldsets = (
        ('Basic Information', {
            'fields': ('farmer', 'category', 'name', 'description')
        }),
        ('Pricing & Quantity', {
            'fields': ('price', 'quantity', 'unit', 'quality_grade')
        }),
        ('Location & Availability', {
            'fields': ('location', 'harvest_date', 'is_available')
        }),
        ('Images', {
            'fields': ('image', 'image_preview', 'image_url'),
            'description': 'Upload product image or provide image URL'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PriceSuggestion)
class PriceSuggestionAdmin(admin.ModelAdmin):
    list_display = ('product', 'suggested_price', 'confidence_score', 'price_label', 'created_at')
    list_filter = ('price_label', 'created_at')
    search_fields = ('product__name',)
    readonly_fields = ('created_at',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'product__name')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username')
    readonly_fields = ('created_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_at',)

@admin.register(MarketTrend)
class MarketTrendAdmin(admin.ModelAdmin):
    list_display = ('category', 'average_price', 'price_trend', 'demand_level', 'created_at')
    list_filter = ('price_trend', 'demand_level', 'created_at')
    search_fields = ('category__name',)
    readonly_fields = ('created_at',)

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'confidence', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'category__name')
    readonly_fields = ('created_at',)
    filter_horizontal = ('recommended_products',)

@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'results_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'query')
    readonly_fields = ('created_at',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('user__username', 'content')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Add these to your existing admin.py

@admin.register(PriceSuggestionRequest)
class PriceSuggestionRequestAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'buyer', 'category', 'suggested_price', 'quantity_needed', 'location', 'urgency', 'status', 'created_at', 'is_expired')
    list_filter = ('status', 'urgency', 'category', 'created_at')
    search_fields = ('product_name', 'buyer__username', 'location')
    list_editable = ('status',)
    readonly_fields = ('created_at',)

@admin.register(FarmerPriceResponse)
class FarmerPriceResponseAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'price_suggestion', 'counter_price', 'available_quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('farmer__username', 'price_suggestion__product_name')
    readonly_fields = ('created_at',)