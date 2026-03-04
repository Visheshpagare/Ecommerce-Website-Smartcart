import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from products.models import Category, Product, ProductImage, Review
from orders.models import Order, OrderItem, Coupon
from users.models import CustomUser, UserProfile


class Command(BaseCommand):
    help = 'Seed database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        self.create_categories()
        self.create_products()
        self.create_users()
        self.create_orders()
        self.create_coupons()
        self.create_reviews()
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_categories(self):
        categories = [
            {'name': 'Electronics', 'slug': 'electronics'},
            {'name': 'Clothing', 'slug': 'clothing'},
            {'name': 'Books', 'slug': 'books'},
            {'name': 'Home & Garden', 'slug': 'home-garden'},
            {'name': 'Sports', 'slug': 'sports'},
        ]
        
        for cat in categories:
            Category.objects.get_or_create(
                slug=cat['slug'],
                defaults={'name': cat['name'], 'slug': cat['slug']}
            )
        
        self.stdout.write('Created categories')

    def create_products(self):
        products_data = [
            # Electronics (4)
            {'name': 'Wireless Bluetooth Headphones', 'slug': 'wireless-headphones', 'price': Decimal('79.99'), 'stock': 50, 'category': 'electronics', 'desc': 'Premium wireless headphones with noise cancellation and 30-hour battery life.'},
            {'name': 'Smart Watch Pro', 'slug': 'smart-watch-pro', 'price': Decimal('199.99'), 'stock': 30, 'category': 'electronics', 'desc': 'Advanced smartwatch with health monitoring, GPS, and water resistance.'},
            {'name': 'Portable Bluetooth Speaker', 'slug': 'bluetooth-speaker', 'price': Decimal('49.99'), 'stock': 75, 'category': 'electronics', 'desc': 'Compact wireless speaker with powerful bass and 12-hour playtime.'},
            {'name': '4K Webcam HD', 'slug': '4k-webcam', 'price': Decimal('89.99'), 'stock': 25, 'category': 'electronics', 'desc': 'High-definition webcam perfect for video calls and streaming.'},
            
            # Clothing (4)
            {'name': 'Premium Cotton T-Shirt', 'slug': 'cotton-tshirt', 'price': Decimal('24.99'), 'stock': 100, 'category': 'clothing', 'desc': '100% organic cotton t-shirt with comfortable fit.'},
            {'name': 'Denim Jeans Classic', 'slug': 'denim-jeans', 'price': Decimal('59.99'), 'stock': 60, 'category': 'clothing', 'desc': 'Classic fit denim jeans with premium quality.'},
            {'name': 'Wool Winter Sweater', 'slug': 'wool-sweater', 'price': Decimal('79.99'), 'stock': 40, 'category': 'clothing', 'desc': 'Warm wool sweater perfect for winter season.'},
            {'name': 'Running Sneakers', 'slug': 'running-sneakers', 'price': Decimal('99.99'), 'stock': 35, 'category': 'clothing', 'desc': 'Lightweight running shoes with cushioned sole.'},
            
            # Books (4)
            {'name': 'Python Programming Guide', 'slug': 'python-guide', 'price': Decimal('39.99'), 'stock': 80, 'category': 'books', 'desc': 'Comprehensive guide to Python programming for beginners.'},
            {'name': 'The Art of Problem Solving', 'slug': 'art-problem-solving', 'price': Decimal('29.99'), 'stock': 45, 'category': 'books', 'desc': 'Master problem-solving techniques with this bestseller.'},
            {'name': 'Web Development Cookbook', 'slug': 'web-dev-cookbook', 'price': Decimal('44.99'), 'stock': 30, 'category': 'books', 'desc': 'Essential recipes for modern web development.'},
            {'name': 'Data Science Handbook', 'slug': 'data-science-handbook', 'price': Decimal('49.99'), 'stock': 25, 'category': 'books', 'desc': 'Complete handbook for aspiring data scientists.'},
            
            # Home & Garden (4)
            {'name': 'Indoor Plant Set', 'slug': 'indoor-plant-set', 'price': Decimal('34.99'), 'stock': 55, 'category': 'home-garden', 'desc': 'Set of 3 beautiful indoor plants with pots.'},
            {'name': 'LED Desk Lamp', 'slug': 'led-desk-lamp', 'price': Decimal('29.99'), 'stock': 70, 'category': 'home-garden', 'desc': 'Adjustable LED desk lamp with touch control.'},
            {'name': 'Cotton Bed Sheets', 'slug': 'cotton-bed-sheets', 'price': Decimal('59.99'), 'stock': 40, 'category': 'home-garden', 'desc': 'Premium Egyptian cotton bed sheets set.'},
            {'name': 'Kitchen Knife Set', 'slug': 'kitchen-knife-set', 'price': Decimal('89.99'), 'stock': 20, 'category': 'home-garden', 'desc': 'Professional 8-piece kitchen knife set.'},
            
            # Sports (4)
            {'name': 'Yoga Mat Premium', 'slug': 'yoga-mat', 'price': Decimal('34.99'), 'stock': 65, 'category': 'sports', 'desc': 'Non-slip yoga mat with carrying strap.'},
            {'name': 'Adjustable Dumbbells', 'slug': 'dumbbells', 'price': Decimal('149.99'), 'stock': 15, 'category': 'sports', 'desc': '5-25lb adjustable dumbbell set.'},
            {'name': 'Tennis Racket Pro', 'slug': 'tennis-racket', 'price': Decimal('89.99'), 'stock': 30, 'category': 'sports', 'desc': 'Professional tennis racket with carbon fiber frame.'},
            {'name': 'Basketball Official', 'slug': 'basketball', 'price': Decimal('29.99'), 'stock': 50, 'category': 'sports', 'desc': 'Official size and weight basketball.'},
        ]
        
        categories = {cat.slug: cat for cat in Category.objects.all()}
        
        for i, data in enumerate(products_data):
            category = categories.get(data['category'])
            if not category:
                continue
            
            product, created = Product.objects.get_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'slug': data['slug'],
                    'description': data['desc'],
                    'price': data['price'],
                    'stock': data['stock'],
                    'category': category,
                    'is_active': True,
                }
            )
            
            if created:
                image_url = f'https://picsum.photos/400/400?random={i+1}'
                try:
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        from django.core.files.base import ContentFile
                        image_name = f"{data['slug']}.jpg"
                        product.image.save(image_name, ContentFile(response.content), save=True)
                except:
                    pass
        
        self.stdout.write('Created products')

    def create_users(self):
        # Superuser
        admin, created = CustomUser.objects.get_or_create(
            email='admin@shop.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            UserProfile.objects.get_or_create(user=admin)
        
        # Customers
        customers = [
            {'username': 'john_doe', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'address': '123 Main St, New York, NY'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'address': '456 Oak Ave, Los Angeles, CA'},
            {'username': 'bob_wilson', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Wilson', 'address': '789 Pine Rd, Chicago, IL'},
        ]
        
        for c in customers:
            user, created = CustomUser.objects.get_or_create(
                email=c['email'],
                defaults={
                    'username': c['username'],
                    'first_name': c['first_name'],
                    'last_name': c['last_name'],
                    'address': c['address'],
                    'city': c['address'].split(',')[-1].strip(),
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                UserProfile.objects.get_or_create(user=user)
        
        self.stdout.write('Created users')

    def create_orders(self):
        users = list(CustomUser.objects.filter(is_staff=False)[:3])
        products = list(Product.objects.all()[:10])
        
        if not users or not products:
            self.stdout.write('Need users and products first')
            return
        
        statuses = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED']
        
        for i, status in enumerate(statuses):
            user = users[i % len(users)]
            order = Order.objects.create(
                user=user,
                total_price=Decimal('0'),
                status=status,
                payment_status='PAID' if status != 'PENDING' else 'PENDING',
                shipping_address=user.address or '123 Test St, Test City, TC',
            )
            
            total = Decimal('0')
            num_items = 2
            
            for j in range(num_items):
                product = products[(i + j) % len(products)]
                quantity = j + 1
                price = product.final_price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                total += price * quantity
            
            order.total_price = total
            order.save()
        
        self.stdout.write('Created orders')

    def create_coupons(self):
        coupons = [
            {'code': 'SAVE10', 'discount_percent': Decimal('10')},
            {'code': 'FLAT20', 'discount_percent': Decimal('20')},
        ]
        
        for c in coupons:
            Coupon.objects.get_or_create(
                code=c['code'],
                defaults={
                    'code': c['code'],
                    'discount_percent': c['discount_percent'],
                    'is_active': True,
                    'expiry_date': timezone.now() + timedelta(days=30)
                }
            )
        
        self.stdout.write('Created coupons')

    def create_reviews(self):
        users = list(CustomUser.objects.filter(is_staff=False)[:3])
        products = list(Product.objects.all()[:10])
        
        if not users or not products:
            return
        
        comments = [
            'Great product! Highly recommended.',
            'Good quality, fast shipping.',
            'Very satisfied with my purchase.',
            'Exactly as described, worth the price.',
            'Good value for money.',
            'Amazing quality!',
            'Exceeded my expectations.',
            'Would buy again.',
            'Pretty good overall.',
            'Decent product, could be better.',
        ]
        
        for i, product in enumerate(products[:10]):
            user = users[i % len(users)]
            Review.objects.get_or_create(
                product=product,
                user=user,
                defaults={
                    'rating': (i % 5) + 1,
                    'comment': comments[i]
                }
            )
        
        self.stdout.write('Created reviews')
