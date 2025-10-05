from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import JsonResponse
import re
from .models import *
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from datetime import timedelta  # Add this import
from .ai_service import AgriAI

def home(request):
    featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:6]
    testimonials = Testimonial.objects.filter(is_approved=True)
    
    context = {
        'featured_products': featured_products,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)

def how_it_works(request):
    return render(request, 'how_it_works.html')

def marketplace(request):
    products = Product.objects.filter(is_available=True)
    categories = ProductCategory.objects.all()
    
    category_filter = request.GET.get('category')
    if category_filter:
        products = products.filter(category_id=category_filter)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'marketplace.html', context)

def pricing(request):
    return render(request, 'pricing.html')

def about(request):
    testimonials = Testimonial.objects.filter(is_approved=True)
    return render(request, 'about.html', {'testimonials': testimonials})

def contact(request):
    if request.method == 'POST':
        # Handle contact form manually without Django forms
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        if name and email and subject and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    return render(request, 'contact.html')

def blog(request):
    return render(request, 'blog.html')

def faq(request):
    return render(request, 'faq.html')

def support(request):
    return render(request, 'support.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def custom_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        # Validate inputs
        errors = []
        if not username:
            errors.append('Username is required.')
        if not password:
            errors.append('Password is required.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'login.html', {
                'username': username,
                'remember_me': remember_me
            })
        
        # Authenticate user - using username only (Django default)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Handle remember me functionality
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 weeks
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Log login history
            LoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )
            
            # Redirect to next page if specified
            next_page = request.GET.get('next')
            if next_page:
                return redirect(next_page)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html', {
                'username': username,
                'remember_me': remember_me
            })
    
    return render(request, 'login.html')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def custom_logout(request):
    logout(request)
    messages.info(request, 'You have been successfully logged out.')
    return redirect('home')

def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Get form data
        user_type = request.POST.get('user_type')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        phone_number = request.POST.get('phone_number')
        location = request.POST.get('location')
        agree_to_terms = request.POST.get('agree_to_terms')
        
        # Validate inputs
        errors = []
        
        # Required fields
        if not user_type:
            errors.append('Please select your user type.')
        if not first_name:
            errors.append('First name is required.')
        if not last_name:
            errors.append('Last name is required.')
        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email is required.')
        if not password1:
            errors.append('Password is required.')
        if not password2:
            errors.append('Please confirm your password.')
        if not phone_number:
            errors.append('Phone number is required.')
        if not location:
            errors.append('Location is required.')
        if not agree_to_terms:
            errors.append('You must agree to the terms and conditions.')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            errors.append('This username is already taken.')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            errors.append('This email is already registered.')
        
        # Password validation
        if password1 and password2:
            if password1 != password2:
                errors.append('Passwords do not match.')
            elif len(password1) < 8:
                errors.append('Password must be at least 8 characters long.')
            elif not re.search(r'[A-Z]', password1) or not re.search(r'[a-z]', password1):
                errors.append('Password must contain both uppercase and lowercase letters.')
            elif not re.search(r'\d', password1):
                errors.append('Password must contain at least one number.')
        
        # Phone number validation
        if phone_number and not re.match(r'^\+?[\d\s-]{10,}$', phone_number):
            errors.append('Please enter a valid phone number.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'signup.html', {
                'user_type': user_type,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'location': location,
                'agree_to_terms': agree_to_terms
            })
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=user_type,
                phone_number=phone_number,
                location=location
            )
            
            # Create security settings
            SecuritySettings.objects.create(user=user)
            
            # Auto-login after signup
            login(request, user)
            messages.success(request, f'Account created successfully! Welcome to AgriLink Market, {first_name}!')
            
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred during registration. Please try again. Error: {str(e)}')
            return render(request, 'signup.html', {
                'user_type': user_type,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'phone_number': phone_number,
                'location': location,
                'agree_to_terms': agree_to_terms
            })
    
    # Pre-fill user type if coming from homepage
    user_type = request.GET.get('type')
    context = {}
    if user_type in ['farmer', 'buyer']:
        context['user_type'] = user_type
    
    return render(request, 'signup.html', context)

@login_required
def dashboard(request):
    """Redirect to appropriate dashboard based on user type"""
    try:
        user_profile = request.user.profile
        if user_profile.user_type == 'buyer':
            return redirect('buyer_dashboard')
        elif user_profile.user_type == 'farmer':
            return redirect('farmer_dashboard')
        else:  # both
            # You can create a combined dashboard or redirect to buyer as default
            return redirect('buyer_dashboard')
    except UserProfile.DoesNotExist:
        # Create default profile and redirect
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type='buyer',
            phone_number='',
            location=''
        )
        return redirect('buyer_dashboard')

@login_required
def buyer_dashboard(request):
    """Enhanced buyer dashboard with price suggestions and orders"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type='buyer',
            phone_number='',
            location=''
        )
    
    # Get buyer-specific data
    buyer_orders = Order.objects.filter(buyer=request.user).order_by('-created_at')[:5]
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')[:6]
    price_suggestions = PriceSuggestionRequest.objects.filter(buyer=request.user).order_by('-created_at')[:5]
    
    # Calculate buyer stats
    total_orders = Order.objects.filter(buyer=request.user).count()
    total_spent = Order.objects.filter(buyer=request.user).aggregate(
        total=models.Sum('total_price')
    )['total'] or 0
    
    active_suggestions = PriceSuggestionRequest.objects.filter(
        buyer=request.user, 
        status='active'
    ).count()
    
    # Get recent market trends for buyer insights
    market_trends = MarketTrend.objects.all().order_by('-created_at')[:3]
    
    # Get AI recommendations for buyer
    ai_recommendations = AgriAI.recommend_products_for_user(request.user)[:4]
    
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')[:5]
    
    context = {
        'user_profile': user_profile,
        'buyer_orders': buyer_orders,
        'wishlist_items': wishlist_items,
        'price_suggestions': price_suggestions,
        'market_trends': market_trends,
        'ai_recommendations': ai_recommendations,
        'login_history': login_history,
        'buyer_stats': {
            'total_orders': total_orders,
            'total_spent': total_spent,
            'active_suggestions': active_suggestions,
            'wishlist_count': wishlist_items.count(),
        }
    }
    
    return render(request, 'buyer_dashboard.html', context)

@login_required
def security_settings(request):
    security_settings, created = SecuritySettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        two_factor_enabled = request.POST.get('two_factor_enabled') == 'on'
        two_factor_method = request.POST.get('two_factor_method', 'email')
        
        security_settings.two_factor_enabled = two_factor_enabled
        security_settings.two_factor_method = two_factor_method
        security_settings.save()
        
        messages.success(request, 'Security settings updated successfully!')
        return redirect('security_settings')
    
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')[:10]
    
    return render(request, 'security_settings.html', {
        'security_settings': security_settings,
        'login_history': login_history
    })

def demo_login(request, demo_type):
    """
    View for demo account logins (for testing purposes)
    """
    # First, ensure demo users exist
    create_demo_users()
    
    demo_accounts = {
        'farmer': {'username': 'demo_farmer', 'password': 'demo1234'},
        'buyer': {'username': 'demo_buyer', 'password': 'demo1234'},
    }
    
    if demo_type in demo_accounts:
        user = authenticate(
            request,
            username=demo_accounts[demo_type]['username'],
            password=demo_accounts[demo_type]['password']
        )
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Demo login successful! Welcome {user.username}.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Demo login failed. Please try again.')
    
    return redirect('login')

def create_demo_users():
    """Create demo users if they don't exist"""
    try:
        # Create demo farmer
        if not User.objects.filter(username='demo_farmer').exists():
            farmer = User.objects.create_user(
                username='demo_farmer',
                email='farmer@agrilink.co.ke',
                password='demo1234',
                first_name='Demo',
                last_name='Farmer'
            )
            UserProfile.objects.create(
                user=farmer,
                user_type='farmer',
                phone_number='+254700000001',
                location='Nakuru'
            )
            SecuritySettings.objects.create(user=farmer)
        
        # Create demo buyer
        if not User.objects.filter(username='demo_buyer').exists():
            buyer = User.objects.create_user(
                username='demo_buyer',
                email='buyer@agrilink.co.ke',
                password='demo1234',
                first_name='Demo',
                last_name='Buyer'
            )
            UserProfile.objects.create(
                user=buyer,
                user_type='buyer',
                phone_number='+254700000002',
                location='Nairobi'
            )
            SecuritySettings.objects.create(user=buyer)
    except Exception as e:
        print(f"Error creating demo users: {e}")

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_available=True)
    price_suggestions = PriceSuggestion.objects.filter(product=product).order_by('-created_at')[:5]
    
    context = {
        'product': product,
        'price_suggestions': price_suggestions,
    }
    return render(request, 'product_detail.html', context)

def get_price_trends(request):
    # This would typically connect to your AI service
    # For now, returning mock data
    trends_data = {
        'maize': [45, 52, 48, 55, 60, 58],
        'tomatoes': [80, 75, 85, 90, 95, 92],
        'potatoes': [35, 40, 38, 42, 45, 43],
    }
    return JsonResponse(trends_data)

from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import json
from .models import Product, ProductCategory, Wishlist, PriceSuggestion, MarketTrend, SearchHistory
from .ai_service import AgriAI

def marketplace(request):
    # Get filter parameters
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    location_filter = request.GET.get('location', '')
    sort_by = request.GET.get('sort_by', 'recommended')
    
    # Start with all available products
    products = Product.objects.filter(is_available=True)
    
    # Apply filters
    if category_filter:
        products = products.filter(category__name__icontains=category_filter)
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
        # Save search history for logged-in users
        if request.user.is_authenticated:
            SearchHistory.objects.create(
                user=request.user,
                query=search_query,
                results_count=products.count()
            )
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    if location_filter and location_filter != 'all':
        products = products.filter(location__icontains=location_filter)
    
    # Apply sorting
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'recent':
        products = products.order_by('-created_at')
    elif sort_by == 'harvest':
        products = products.order_by('harvest_date')
    else:  # recommended (default)
        # Sort by AI confidence score if available
        products = products.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-avg_rating', '-review_count')
    
    # Generate AI price suggestions for products
    for product in products:
        if not hasattr(product, 'ai_suggestion'):
            price_data = AgriAI.calculate_optimal_price(product)
            product.ai_suggestion = price_data
    
    # Pagination
    paginator = Paginator(products, 12)  # 12 products per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = ProductCategory.objects.all()
    
    # Get market trends and recommendations
    market_trends = MarketTrend.objects.all().order_by('-created_at')[:3]
    ai_recommendations = AgriAI.generate_market_recommendations()
    
    # Get user's wishlist if logged in
    wishlist_product_ids = []
    if request.user.is_authenticated:
        wishlist_product_ids = Wishlist.objects.filter(
            user=request.user
        ).values_list('product_id', flat=True)
    
    context = {
        'products': page_obj,
        'categories': categories,
        'market_trends': market_trends,
        'ai_recommendations': ai_recommendations,
        'wishlist_product_ids': wishlist_product_ids,
        'current_filters': {
            'category': category_filter,
            'search': search_query,
            'min_price': min_price,
            'max_price': max_price,
            'location': location_filter,
            'sort_by': sort_by,
        },
        'stats': {
            'total_products': products.count(),
            'active_farmers': User.objects.filter(products__is_available=True).distinct().count(),
            'counties_covered': products.values('location').distinct().count(),
        }
    }
    
    return render(request, 'marketplace.html', context)

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f'{product.name} added to your wishlist!')
    else:
        wishlist_item.delete()
        messages.info(request, f'{product.name} removed from your wishlist!')
    
    return redirect('marketplace')

@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # In a real implementation, this would create an order
    # For now, we'll just show a success message
    messages.success(
        request, 
        f'Order placed for {product.name}! The farmer will contact you soon.'
    )
    
    return redirect('marketplace')

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Generate AI price suggestion
    ai_suggestion = AgriAI.calculate_optimal_price(product)
    
    # Get similar products
    similar_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product_id)[:4]
    
    # Get reviews
    reviews = product.reviews.all().order_by('-created_at')
    
    context = {
        'product': product,
        'ai_suggestion': ai_suggestion,
        'similar_products': similar_products,
        'reviews': reviews,
    }
    
    return render(request, 'product_detail.html', context)

def ai_recommendations_api(request):
    """API endpoint for AI recommendations"""
    if request.user.is_authenticated:
        recommendations = AgriAI.recommend_products_for_user(request.user)
    else:
        # For non-logged in users, show popular products
        recommendations = Product.objects.filter(
            is_available=True
        ).annotate(
            review_count=Count('reviews')
        ).order_by('-review_count')[:6]
    
    data = {
        'recommendations': [
            {
                'id': product.id,
                'name': product.name,
                'price': float(product.price),
                'category': product.category.name,
                'location': product.location,
                'image_url': product.image_url,
            }
            for product in recommendations
        ]
    }
    
    return JsonResponse(data)

def update_market_trends(request):
    """Admin function to update market trends (would be called periodically)"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    categories = ProductCategory.objects.all()
    
    for category in categories:
        # Calculate average price for category
        products = Product.objects.filter(category=category, is_available=True)
        if products.exists():
            avg_price = sum(float(p.price) for p in products) / products.count()
            
            # Simple trend calculation (in real app, use historical data)
            previous_trend = MarketTrend.objects.filter(
                category=category
            ).order_by('-created_at').first()
            
            if previous_trend:
                if avg_price > float(previous_trend.average_price) * 1.05:
                    trend = 'increasing'
                elif avg_price < float(previous_trend.average_price) * 0.95:
                    trend = 'decreasing'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Demand level based on number of products
            if products.count() > 20:
                demand = 'high'
            elif products.count() > 10:
                demand = 'medium'
            else:
                demand = 'low'
            
            # Create recommendation
            if trend == 'increasing' and demand == 'high':
                recommendation = f"High demand for {category.name}. Prices rising. Good time to sell."
            elif trend == 'decreasing' and demand == 'low':
                recommendation = f"Low demand for {category.name}. Prices falling. Good time to buy."
            else:
                recommendation = f"Market for {category.name} is stable. Good time for trading."
            
            MarketTrend.objects.create(
                category=category,
                average_price=avg_price,
                price_trend=trend,
                demand_level=demand,
                recommendation=recommendation
            )
    
    return JsonResponse({'status': 'Market trends updated successfully'})

# Add these views to your existing views.py

@login_required
def price_suggestions_marketplace(request):
    """View for buyers to see and create price suggestions"""
    active_suggestions = PriceSuggestionRequest.objects.filter(
        status='active',
        expires_at__gt=timezone.now()
    ).order_by('-created_at')
    
    # Get user's own suggestions
    user_suggestions = PriceSuggestionRequest.objects.filter(
        buyer=request.user
    ).order_by('-created_at')
    
    categories = ProductCategory.objects.all()
    
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        suggested_price = request.POST.get('suggested_price')
        quantity_needed = request.POST.get('quantity_needed')
        unit = request.POST.get('unit')
        location = request.POST.get('location')
        urgency = request.POST.get('urgency')
        description = request.POST.get('description')
        
        # Validate required fields
        errors = []
        if not product_name:
            errors.append('Product name is required.')
        if not category_id:
            errors.append('Category is required.')
        if not suggested_price:
            errors.append('Suggested price is required.')
        if not location:
            errors.append('Location is required.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'price_suggestions_marketplace.html', {
                'active_suggestions': active_suggestions,
                'user_suggestions': user_suggestions,
                'categories': categories,
            })
        
        try:
            category = ProductCategory.objects.get(id=category_id)
            suggestion = PriceSuggestionRequest.objects.create(
                buyer=request.user,
                category=category,
                product_name=product_name,
                suggested_price=suggested_price,
                quantity_needed=quantity_needed,
                unit=unit,
                location=location,
                urgency=urgency,
                description=description,
                expires_at=timezone.now() + timedelta(days=7)  # Expires in 7 days
            )
            messages.success(request, 'Price suggestion posted successfully! Farmers will see your request.')
            return redirect('price_suggestions_marketplace')
        except Exception as e:
            messages.error(request, f'Error creating price suggestion: {str(e)}')
    
    context = {
        'active_suggestions': active_suggestions,
        'user_suggestions': user_suggestions,
        'categories': categories,
    }
    return render(request, 'price_suggestions_marketplace.html', context)

@login_required
def farmer_dashboard(request):
    """Enhanced farmer dashboard with price suggestions"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(
            user=request.user,
            user_type='farmer',
            phone_number='',
            location=''
        )
    
    # Only show farmer-specific data if user is a farmer
    farmer_products = Product.objects.filter(farmer=request.user)[:5]
    
    # Get relevant price suggestions for the farmer
    farmer_location = user_profile.location
    relevant_suggestions = PriceSuggestionRequest.objects.filter(
        status='active',
        expires_at__gt=timezone.now()
    ).filter(
        Q(location__icontains=farmer_location) | Q(location='all')
    ).order_by('-created_at')[:10]
    
    # Get farmer's responses
    farmer_responses = FarmerPriceResponse.objects.filter(
        farmer=request.user
    ).order_by('-created_at')[:5]
    
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-login_time')[:5]
    
    context = {
        'user_profile': user_profile,
        'farmer_products': farmer_products,
        'price_suggestions': relevant_suggestions,
        'farmer_responses': farmer_responses,
        'login_history': login_history,
    }
    
    return render(request, 'farmer_dashboard.html', context)

@login_required
def respond_to_price_suggestion(request, suggestion_id):
    """View for farmers to respond to price suggestions"""
    suggestion = get_object_or_404(PriceSuggestionRequest, id=suggestion_id, status='active')
    
    # Check if user is a farmer
    try:
        user_profile = request.user.profile
        if user_profile.user_type not in ['farmer', 'both']:
            messages.error(request, 'Only farmers can respond to price suggestions.')
            return redirect('price_suggestions_marketplace')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile to respond to price suggestions.')
        return redirect('price_suggestions_marketplace')
    
    if request.method == 'POST':
        counter_price = request.POST.get('counter_price')
        available_quantity = request.POST.get('available_quantity')
        message = request.POST.get('message')
        
        # Validate form data
        errors = []
        if not available_quantity or float(available_quantity) <= 0:
            errors.append('Please enter a valid quantity.')
        if not message or not message.strip():
            errors.append('Please enter a message to the buyer.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                response = FarmerPriceResponse.objects.create(
                    farmer=request.user,
                    price_suggestion=suggestion,
                    counter_price=counter_price if counter_price else None,
                    available_quantity=available_quantity,
                    message=message,
                    status='countered' if counter_price and float(counter_price) != float(suggestion.suggested_price) else 'pending'
                )
                messages.success(request, 'Your response has been sent to the buyer!')
                return redirect('farmer_dashboard')
            except Exception as e:
                messages.error(request, f'Error sending response: {str(e)}')
    
    context = {
        'suggestion': suggestion,
    }
    return render(request, 'respond_to_suggestion.html', context)

@login_required
def buyer_price_suggestions(request):
    """View for buyers to manage their price suggestions"""
    user_suggestions = PriceSuggestionRequest.objects.filter(buyer=request.user).order_by('-created_at')
    
    context = {
        'user_suggestions': user_suggestions,
    }
    return render(request, 'buyer_price_suggestions.html', context)

@login_required
def add_product(request):
    """View for farmers to add new products"""
    # Check if user is a farmer
    try:
        user_profile = request.user.profile
        if user_profile.user_type not in ['farmer', 'both']:
            messages.error(request, 'Only farmers can add products.')
            return redirect('dashboard')
    except UserProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile to add products.')
        return redirect('security_settings')
    
    categories = ProductCategory.objects.all()
    
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        unit = request.POST.get('unit')
        quality_grade = request.POST.get('quality_grade')
        location = request.POST.get('location')
        harvest_date = request.POST.get('harvest_date')
        image = request.FILES.get('image')
        
        # Validate required fields
        errors = []
        if not name:
            errors.append('Product name is required.')
        if not category_id:
            errors.append('Category is required.')
        if not description:
            errors.append('Description is required.')
        if not price or float(price) <= 0:
            errors.append('Valid price is required.')
        if not quantity or float(quantity) <= 0:
            errors.append('Valid quantity is required.')
        if not location:
            errors.append('Location is required.')
        if not harvest_date:
            errors.append('Harvest date is required.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                category = ProductCategory.objects.get(id=category_id)
                
                # Create the product
                product = Product.objects.create(
                    farmer=request.user,
                    category=category,
                    name=name,
                    description=description,
                    price=price,
                    quantity=quantity,
                    unit=unit,
                    quality_grade=quality_grade,
                    location=location,
                    harvest_date=harvest_date,
                    image=image,
                    is_available=True
                )
                
                # Generate AI price suggestion
                ai_suggestion = AgriAI.calculate_optimal_price(product)
                PriceSuggestion.objects.create(
                    product=product,
                    suggested_price=ai_suggestion['suggested_price'],
                    confidence_score=ai_suggestion['confidence_score'],
                    factors_considered=ai_suggestion['factors_considered'],
                    price_label=ai_suggestion['price_label']
                )
                
                messages.success(request, f'Product "{name}" added successfully! AI price analysis completed.')
                return redirect('farmer_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error adding product: {str(e)}')
    
    # Get AI recommendations for similar products
    similar_products = Product.objects.filter(
        farmer=request.user,
        is_available=True
    ).order_by('-created_at')[:3]
    
    context = {
        'categories': categories,
        'similar_products': similar_products,
        'quality_grades': ['premium', 'grade1', 'grade2', 'standard'],
        'units': ['kg', 'g', 'ton', 'bag', 'crate', 'piece', 'bunch'],
    }
    
    return render(request, 'add_product.html', context)