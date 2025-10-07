AgriLink Market 🌱

A comprehensive farmer-to-buyer agricultural marketplace platform that connects Kenyan farmers directly with buyers using AI-powered pricing and recommendations.
Table of Contents

-Features
-Technology Stack
-Installation
-Project Structure
-Database Models
-API Endpoints
-AI Features
-Screenshots
-Contributing
-License
-Features


🎯 Core Functionality

-Multi-user System: Farmers, Buyers, and Both roles
-Product Marketplace: Browse, search, and filter agricultural products
-AI-Powered Pricing: Smart price suggestions using machine learning
-Price Suggestions: Buyers can suggest prices to farmers
-Wishlist & Orders: Save products and place orders
-Market Trends: Real-time market insights and analytics
-Secure Authentication: User registration, login, and security settings


🤖 AI-Powered Features

-Optimal Price Calculation: AI suggests best prices based on market data
-Personalized Recommendations: Product suggestions based on user behavior
-Market Trend Analysis: Predictive analytics for price trends
-Demand Forecasting: AI predicts product demand patterns


💼 User Dashboards

-Farmer Dashboard: Manage products, view price suggestions, track orders
-Buyer Dashboard: Browse products, suggest prices, track purchases
-Admin Panel: Comprehensive management with Jazzmin interface


Technology Stack

Backend

Django 4.2+: Python web framework
Django REST Framework: API development
PostgreSQL: Database (production)
SQLite: Database (development)
-Pillow: Image processing
-Jazzmin: Admin interface customization


Frontend

-HTML5/CSS3: Responsive design
-JavaScript: Interactive features
-Font Awesome: Icons
-Custom CSS: Professional styling


AI/ML

-Custom AI Service: Price optimization algorithms
-Market Analysis: Trend prediction models
-Recommendation Engine: Personalized suggestions


Installation
Prerequisites

Python 3.8+
PostgreSQL (optional, SQLite for development)


Virtual Environment

Setup Instructions

Clone the Repository
bash
    
    git clone https://github.com/Salvatore-droid/agrilink.git
    cd agrilink-market

Create Virtual Environment
bash
    
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

Install Dependencies
bash

    pip install -r requirements.txt

Environment Configuration
bash

    cp .env.example .env
    # Edit .env with your configuration

Database Setup
bash
    
    python manage.py makemigrations
    python manage.py migrate

Create Superuser
bash

    python manage.py createsuperuser

Load Sample Data (Optional)
bash

    python manage.py loaddata sample_data.json

Run Development Server
bash

    python manage.py runserver

Visit http://localhost:8000 to view the application.
Project Structure
text
    
    agrilink-market/
    ├── base/                          # Main Django app
    │   ├── models.py                  # Database models
    │   ├── views.py                   # Application views
    │   ├── urls.py                    # URL routing
    │   ├── admin.py                   # Admin configuration
    │   ├── ai_service.py              # AI algorithms
    │   └── templates/                 # HTML templates
    ├── static/                        # Static files
    │   ├── css/                       # Stylesheets
    │   ├── js/                        # JavaScript files
    │   └── images/                    # Images and icons
    ├── media/                         # User uploaded files
    ├── requirements.txt               # Python dependencies
    └── manage.py                      # Django management script

Database Models
Core Models

-UserProfile: Extended user information with farmer/buyer roles
-Product: Agricultural products with pricing and availability
-ProductCategory: Product categorization
-Order: Purchase orders and transactions
-PriceSuggestion: AI-generated price recommendations


Authentication & Security

-LoginHistory: User login tracking
-SecuritySettings: Two-factor authentication and security preferences
-PasswordResetToken: Secure password reset functionality


Marketplace Features

-Wishlist: User saved products
-ProductReview: Customer reviews and ratings
-MarketTrend: Market analysis data
-PriceSuggestionRequest: Buyer price requests to farmers
-FarmerPriceResponse: Farmer responses to price suggestions


AI & Analytics

-AIRecommendation: Personalized product suggestions
-SearchHistory: User search behavior tracking
-PriceSuggestion: AI-generated pricing insights


API Endpoints
Authentication

  POST /api/login/ - User authentication
  POST /api/logout/ - User logout
  POST /api/register/ - User registration


Products

  GET /api/products/ - List all products
  POST /api/products/ - Create new product (farmers)
  GET /api/products/{id}/ - Product details
  PUT /api/products/{id}/ - Update product


AI Features

  GET /api/ai-recommendations/ - Personalized recommendations
  GET /api/price-suggestions/ - AI price suggestions
  POST /api/market-trends/ - Market analysis data


Orders & Marketplace

  GET /api/orders/ - User orders
  POST /api/orders/ - Create new order
  GET /api/wishlist/ - User wishlist
  POST /api/wishlist/{product_id}/ - Add to wishlist


AI Features
Price Optimization
python

# Example usage
suggestion = AgriAI.calculate_optimal_price(product)
# Returns: {suggested_price, confidence_score, price_label, factors_considered}

Product Recommendations
python

recommendations = AgriAI.recommend_products_for_user(user)
# Returns personalized product suggestions

Market Analysis
python

trends = AgriAI.generate_market_recommendations()
# Returns market insights and predictions

Screenshots
User Interfaces

    Homepage: Modern landing page with features overview

    Marketplace: Product browsing with advanced filtering

    Farmer Dashboard: Product management and price suggestions

    Buyer Dashboard: Order tracking and price requests

    Admin Panel: Professional management interface

Key Features

    Product listing with AI price suggestions

    Price suggestion marketplace

    Responsive design for all devices

    Professional toast notifications

    Secure user authentication

Contributing

We welcome contributions! Please follow these steps:

    Fork the repository

    Create a feature branch (git checkout -b feature/AmazingFeature)

    Commit your changes (git commit -m 'Add some AmazingFeature')

    Push to the branch (git push origin feature/AmazingFeature)

    Open a Pull Request

Development Guidelines

    Follow PEP 8 Python style guide

    Write tests for new features

    Update documentation accordingly

    Use meaningful commit messages

License

This project is licensed under the MIT License - see the LICENSE file for details.
Support

For support and questions:

  Email: geniusokwemba53@gmail.com
  Issues: GitHub Issues
  Documentation: Project Wiki


Acknowledgments

  Kenyan Agricultural Board for market data insights
  Django community for excellent documentation
  Font Awesome for beautiful icons
  Contributors and testers
  

AgriLink Market - Transforming agriculture through technology, connecting farmers directly to buyers for mutual benefit. 🌱🚀
