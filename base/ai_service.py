import random
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Product, MarketTrend, PriceSuggestion, ProductCategory

class AgriAI:
    @staticmethod
    def calculate_optimal_price(product):
        """Calculate optimal price based on market trends, quality, and other factors"""
        
        # Get market trends for the product category
        try:
            market_trend = MarketTrend.objects.filter(
                category=product.category
            ).order_by('-created_at').first()
        except MarketTrend.DoesNotExist:
            market_trend = None
        
        base_price = float(product.price)
        
        # Quality multiplier
        quality_multipliers = {
            'premium': 1.4,
            'grade1': 1.2,
            'grade2': 1.0,
            'standard': 0.8
        }
        
        # Location adjustment (simplified)
        location_multipliers = {
            'nairobi': 1.1,
            'mombasa': 1.05,
            'nakuru': 0.95,
            'eldoret': 0.9,
            'kisumu': 0.95
        }
        
        # Seasonality factor (simplified)
        current_month = datetime.now().month
        if current_month in [12, 1, 2]:  # Dry season
            season_multiplier = 1.15
        elif current_month in [6, 7, 8]:  # Rainy season
            season_multiplier = 0.9
        else:
            season_multiplier = 1.0
        
        # Calculate suggested price
        quality_multiplier = quality_multipliers.get(product.quality_grade, 1.0)
        location_multiplier = 1.0
        for location, multiplier in location_multipliers.items():
            if location in product.location.lower():
                location_multiplier = multiplier
                break
        
        suggested_price = base_price * quality_multiplier * location_multiplier * season_multiplier
        
        # Adjust based on market trend
        if market_trend:
            if market_trend.price_trend == 'increasing':
                suggested_price *= 1.05
            elif market_trend.price_trend == 'decreasing':
                suggested_price *= 0.95
        
        # Add some randomness for realism
        suggested_price *= random.uniform(0.95, 1.05)
        
        # Round to nearest 10
        suggested_price = round(suggested_price / 10) * 10
        
        # Determine price label
        price_diff = ((suggested_price - base_price) / base_price) * 100
        
        if price_diff <= -10:
            price_label = 'best_price'
        elif price_diff <= -5:
            price_label = 'good_price'
        elif price_diff <= 5:
            price_label = 'fair_price'
        else:
            price_label = 'high_price'
        
        factors = {
            'quality_grade': product.quality_grade,
            'location': product.location,
            'seasonality': current_month,
            'market_trend': market_trend.price_trend if market_trend else 'stable',
            'original_price': float(base_price),
            'price_difference_percent': round(price_diff, 2)
        }
        
        return {
            'suggested_price': suggested_price,
            'confidence_score': random.uniform(0.7, 0.95),
            'price_label': price_label,
            'factors_considered': factors
        }

    @staticmethod
    def generate_market_recommendations():
        """Generate market-wide recommendations"""
        recommendations = []
        categories = ProductCategory.objects.all()
        
        for category in categories:
            # Get recent products in this category
            recent_products = Product.objects.filter(
                category=category,
                is_available=True,
                harvest_date__gte=timezone.now().date()
            ).order_by('price')[:5]
            
            if recent_products:
                avg_price = sum(float(p.price) for p in recent_products) / len(recent_products)
                
                # Simple recommendation logic
                if avg_price < 100:
                    recommendation = f"Great time to buy {category.name.lower()}! Prices are very competitive."
                elif len(recent_products) > 10:
                    recommendation = f"Good supply of {category.name.lower()} available. Prices are stable."
                else:
                    recommendation = f"Limited {category.name.lower()} available. Consider alternatives."
                
                recommendations.append({
                    'category': category.name,
                    'recommendation': recommendation,
                    'average_price': avg_price,
                    'product_count': len(recent_products)
                })
        
        return recommendations

    @staticmethod
    def recommend_products_for_user(user, limit=6):
        """Generate personalized product recommendations for a user"""
        
        # Get user's wishlist and search history
        wishlist_products = Product.objects.filter(wishlist__user=user)
        search_history = SearchHistory.objects.filter(user=user).order_by('-created_at')[:5]
        
        recommended_products = []
        
        # Based on wishlist
        if wishlist_products.exists():
            similar_categories = wishlist_products.values_list('category', flat=True).distinct()
            similar_products = Product.objects.filter(
                category__in=similar_categories,
                is_available=True
            ).exclude(wishlist__user=user).order_by('?')[:limit]
            recommended_products.extend(list(similar_products))
        
        # Based on search history
        if search_history.exists():
            recent_searches = [sh.query for sh in search_history]
            for search_query in recent_searches:
                searched_products = Product.objects.filter(
                    name__icontains=search_query,
                    is_available=True
                ).exclude(id__in=[p.id for p in recommended_products])[:2]
                recommended_products.extend(list(searched_products))
        
        # Fill with popular products if needed
        if len(recommended_products) < limit:
            popular_products = Product.objects.filter(
                is_available=True
            ).annotate(
                review_count=models.Count('reviews')
            ).order_by('-review_count')[:limit - len(recommended_products)]
            recommended_products.extend(list(popular_products))
        
        return list(set(recommended_products))[:limit]