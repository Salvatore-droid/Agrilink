from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('login/', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('demo-login/<str:demo_type>/', views.demo_login, name='demo_login'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='agrilink/password_reset.html',
             email_template_name='agrilink/password_reset_email.html',
             subject_template_name='agrilink/password_reset_subject.txt'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='agrilink/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='agrilink/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='agrilink/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Dashboard and Security
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buyer-dashboard/', views.buyer_dashboard, name='buyer_dashboard'),
    path('security-settings/', views.security_settings, name='security_settings'),
    
    # Other URLs (from previous implementation)
    path('', views.home, name='home'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('pricing/', views.pricing, name='pricing'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path('faq/', views.faq, name='faq'),
    path('support/', views.support, name='support'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('api/price-trends/', views.get_price_trends, name='price_trends'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('marketplace/product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('marketplace/wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('marketplace/buy/<int:product_id>/', views.buy_product, name='buy_product'),
    path('api/ai-recommendations/', views.ai_recommendations_api, name='ai_recommendations_api'),
    path('admin/update-market-trends/', views.update_market_trends, name='update_market_trends'),

    path('farmer/add-product/', views.add_product, name='add_product'),
    path('price-suggestions/', views.price_suggestions_marketplace, name='price_suggestions_marketplace'),
    path('farmer-dashboard/', views.farmer_dashboard, name='farmer_dashboard'),
    path('respond-to-suggestion/<int:suggestion_id>/', views.respond_to_price_suggestion, name='respond_to_suggestion'),
    path('buyer-suggestions/', views.buyer_price_suggestions, name='buyer_price_suggestions'),

     # Groq AI URLs
    # path('negotiate/<int:product_id>/', views.start_negotiation, name='start_negotiation'),
    # path('api/market-insights/', views.get_market_insights, name='market_insights'),
    # path('api/personalized-recommendations/', views.get_personalized_recommendations_api, name='personalized_recommendations'),
]