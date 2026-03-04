# Ecommerce Project

A full-featured Django ecommerce application with products, users, orders, cart, and admin dashboard.

## Features

- User authentication (register, login, logout)
- Product catalog with categories, search, and filtering
- Shopping cart with session and database storage
- Order management and checkout
- Customer dashboard (profile, orders, wishlist)
- Admin dashboard with stats, charts, and management
- Product reviews and ratings
- Coupon codes

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ecommerce

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Seed database with sample data
python manage.py seed_data

# Run development server
python manage.py runserver
```

## Access

- **Homepage:** http://localhost:8000/
- **Admin Panel:** http://localhost:8000/dashboard/
- **Login:** http://localhost:8000/users/login/

## Demo Accounts

### Admin
- Email: admin@shop.com
- Password: admin123

### Customer
- Email: john@example.com
- Password: password123

## Project Structure

```
ecommerce/
├── products/          # Product catalog app
├── users/            # User authentication app
├── orders/           # Cart and orders app
├── dashboard/        # Admin dashboard app
├── templates/        # HTML templates
├── static/           # CSS and JS files
└── media/            # Uploaded images
```

## Available Commands

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Seed database
python manage.py seed_data

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

## Technology Stack

- Django 4.2+
- Python 3.11+
- SQLite (development)
- Tailwind CSS
- Chart.js

## License

MIT License
