# Ecommerce Website Smartcart

A full-featured Django ecommerce application with products, users, orders, cart, and admin dashboard with Razorpay payment integration.

## Features

- User authentication (register, login, logout)
- Product catalog with categories, search, and filtering
- Shopping cart with session and database storage
- Order management and checkout
- Customer dashboard (profile, orders, wishlist)
- Admin dashboard with stats and charts
- Product reviews and ratings
- Coupon codes
- Razorpay payment integration

## Installation

```bash
# Clone the repository
git clone <repository-url>

# Move into project folder
cd ecommerce

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver