import os
import json
import random
from datetime import datetime
from groq import Groq
from django.conf import settings
from .models import Product, MarketTrend, ProductCategory

class GroqAIService:
    def __init__(self):
        # Initialize Groq client - you'll need to set GROQ_API_KEY in your environment
        self.client = Groq(api_key=os.environ.get('GROQ_API_KEY', 'your-groq-api-key-here'))
        self.model = "llama3-8b-8192"  # You can use other models like "mixtral-8x7b-32768"

    def get_price_recommendation(self, product, market_context=None):
        """
        Get AI-powered price recommendation using Groq
        """
        try:
            # Prepare product context
            product_context = {
                'name': product.name,
                'category': product.category.name,
                'current_price': float(product.price),
                'quality_grade': product.quality_grade,
                'location': product.location,
                'harvest_date': product.harvest_date.isoformat(),
                'quantity': float(product.quantity),
                'unit': product.unit
            }
            
            # Get market trends if available
            if not market_context:
                market_context = self.get_market_context(product.category)
            
            prompt = self._create_price_recommendation_prompt(product_context, market_context)
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": """You are an agricultural market expert specializing in price optimization for fresh produce in Kenya. 
                        Analyze market data and provide intelligent price recommendations considering quality, location, seasonality, and demand."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=500
            )
            
            return self._parse_price_recommendation(response.choices[0].message.content, product_context)
            
        except Exception as e:
            # Fallback to basic algorithm if Groq fails
            print(f"Groq API error: {e}")
            return self._fallback_price_calculation(product)

    def get_negotiation_strategy(self, product, buyer_profile, initial_offer):
        """
        Get AI-powered negotiation strategy
        """
        try:
            prompt = f"""
            Product: {product.name}
            Category: {product.category.name}
            Current Price: KES {product.price}
            Quality: {product.quality_grade}
            Location: {product.location}
            
            Buyer Offer: KES {initial_offer}
            Buyer Type: {buyer_profile.get('type', 'unknown')}
            
            As an agricultural negotiation expert, provide:
            1. Recommended counter-offer price
            2. Negotiation strategy points
            3. Key value propositions to emphasize
            4. Potential compromise points
            
            Respond in JSON format with: counter_offer, strategy_points, value_propositions, compromise_points
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert agricultural negotiator helping farmers get fair prices while maintaining good buyer relationships."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Groq negotiation error: {e}")
            return self._fallback_negotiation_strategy(product, initial_offer)

    def get_market_insights(self, category=None):
        """
        Get AI-powered market insights and recommendations
        """
        try:
            market_data = self.get_market_context(category)
            
            prompt = f"""
            Current Market Data:
            {json.dumps(market_data, indent=2)}
            
            Provide:
            1. Current market analysis
            2. Price trend predictions for the next week
            3. Buying/selling recommendations
            4. Key factors affecting prices
            
            Respond in a structured format suitable for farmers and buyers.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an agricultural market analyst providing insights for Kenyan farmers and buyers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Groq market insights error: {e}")
            return "Market insights currently unavailable. Please check back later."

    def get_personalized_recommendations(self, user, search_history, wishlist):
        """
        Get personalized product recommendations
        """
        try:
            user_context = {
                'user_type': user.profile.user_type if hasattr(user, 'profile') else 'buyer',
                'location': user.profile.location if hasattr(user, 'profile') else 'Nairobi',
                'recent_searches': [sh.query for sh in search_history],
                'wishlist_items': [item.product.name for item in wishlist]
            }
            
            prompt = f"""
            User Profile:
            {json.dumps(user_context, indent=2)}
            
            Based on this user's profile and behavior, recommend:
            1. Products they might be interested in
            2. Optimal buying/selling timing
            3. Price alerts to set
            4. Market opportunities
            
            Provide specific, actionable recommendations.
            """
            
            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a personalized agricultural shopping assistant for Kenyan farmers and buyers."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=600
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Groq recommendations error: {e}")
            return "Personalized recommendations currently unavailable."

    def _create_price_recommendation_prompt(self, product_context, market_context):
        return f"""
        Analyze this agricultural product and provide price optimization advice:

        PRODUCT DETAILS:
        - Name: {product_context['name']}
        - Category: {product_context['category']}
        - Current Price: KES {product_context['current_price']}
        - Quality Grade: {product_context['quality_grade']}
        - Location: {product_context['location']}
        - Harvest Date: {product_context['harvest_date']}
        - Quantity: {product_context['quantity']} {product_context['unit']}

        MARKET CONTEXT:
        - Average Market Price: KES {market_context.get('average_price', 'N/A')}
        - Price Trend: {market_context.get('price_trend', 'stable')}
        - Demand Level: {market_context.get('demand_level', 'medium')}
        - Season: {self._get_current_season()}

        Please provide:
        1. Recommended optimal price (KES)
        2. Price confidence score (0-1)
        3. Price label (best_price, good_price, fair_price, high_price)
        4. Key factors influencing this recommendation
        5. Brief explanation

        Respond in JSON format with: suggested_price, confidence_score, price_label, factors, explanation
        """

    def _parse_price_recommendation(self, response_text, product_context):
        try:
            # Try to parse JSON response
            data = json.loads(response_text)
            return {
                'suggested_price': float(data.get('suggested_price', product_context['current_price'])),
                'confidence_score': float(data.get('confidence_score', 0.7)),
                'price_label': data.get('price_label', 'fair_price'),
                'factors_considered': data.get('factors', {}),
                'explanation': data.get('explanation', 'AI price recommendation')
            }
        except:
            # Fallback if JSON parsing fails
            return self._fallback_price_calculation_from_context(product_context)

    def get_market_context(self, category):
        """Get current market context for a category"""
        try:
            if category:
                trend = MarketTrend.objects.filter(category=category).order_by('-created_at').first()
                if trend:
                    return {
                        'average_price': float(trend.average_price),
                        'price_trend': trend.price_trend,
                        'demand_level': trend.demand_level,
                        'recommendation': trend.recommendation
                    }
            
            # Default market context
            return {
                'average_price': random.uniform(50, 500),
                'price_trend': random.choice(['increasing', 'decreasing', 'stable']),
                'demand_level': random.choice(['high', 'medium', 'low']),
                'recommendation': 'Monitor market trends for optimal pricing'
            }
        except:
            return {
                'average_price': 150,
                'price_trend': 'stable',
                'demand_level': 'medium',
                'recommendation': 'Standard market conditions'
            }

    def _get_current_season(self):
        """Get current season in Kenya"""
        month = datetime.now().month
        if month in [12, 1, 2]:  # Dry season
            return "Dry Season (High prices expected)"
        elif month in [3, 4, 5]:  # Long rains
            return "Long Rains Season"
        elif month in [6, 7, 8]:  # Cold season
            return "Cold Season"
        else:  # Short rains
            return "Short Rains Season"

    def _fallback_price_calculation(self, product):
        """Fallback price calculation if Groq fails"""
        base_price = float(product.price)
        
        # Simple quality multipliers
        quality_multipliers = {
            'premium': 1.3,
            'grade1': 1.15,
            'grade2': 1.0,
            'standard': 0.85
        }
        
        multiplier = quality_multipliers.get(product.quality_grade, 1.0)
        suggested_price = base_price * multiplier * random.uniform(0.9, 1.1)
        
        return {
            'suggested_price': round(suggested_price, 2),
            'confidence_score': 0.6,
            'price_label': 'fair_price',
            'factors_considered': {
                'quality_grade': product.quality_grade,
                'fallback_calculation': True
            },
            'explanation': 'Basic price calculation applied'
        }

    def _fallback_price_calculation_from_context(self, product_context):
        """Fallback using product context"""
        return self._fallback_price_calculation(type('MockProduct', (), {
            'price': product_context['current_price'],
            'quality_grade': product_context['quality_grade']
        })())

    def _fallback_negotiation_strategy(self, product, initial_offer):
        """Fallback negotiation strategy"""
        current_price = float(product.price)
        buyer_offer = float(initial_offer)
        
        if buyer_offer >= current_price * 0.9:
            counter_offer = current_price * 0.95
        else:
            counter_offer = current_price * 0.85
            
        return {
            'counter_offer': round(counter_offer, 2),
            'strategy_points': [
                'Emphasize product quality and freshness',
                'Highlight direct farmer-to-buyer advantage',
                'Consider bulk purchase discounts'
            ],
            'value_propositions': [
                f'Fresh {product.quality_grade} quality {product.name}',
                f'Harvested on {product.harvest_date}',
                'Direct from farm pricing'
            ],
            'compromise_points': [
                'Flexible on delivery timing',
                'Bulk order discounts available',
                'Repeat customer benefits'
            ]
        }

# Global instance
groq_ai = GroqAIService()