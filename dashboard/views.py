from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from products.models import Product, Category
from orders.models import Order, OrderItem, Coupon
from users.models import CustomUser
from .decorators import staff_required


@staff_required
def dashboard_home(request):
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    total_revenue = Order.objects.filter(
        status='DELIVERED'
    ).aggregate(total=Sum('total_price'))['total'] or Decimal('0')
    
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=today).count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    
    total_products = Product.objects.count()
    total_users = CustomUser.objects.count()
    low_stock_products = Product.objects.filter(stock__lt=10)
    
    recent_orders = Order.objects.order_by('-created_at')[:10]
    
    top_products = Product.objects.annotate(
        total_sold=Sum('orderitem__quantity')
    ).filter(total_sold__gt=0).order_by('-total_sold')[:5]
    
    return render(request, 'dashboard/home.html', {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'pending_orders': pending_orders,
        'total_products': total_products,
        'total_users': total_users,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'top_products': top_products,
    })


@staff_required
def product_list(request):
    products = Product.objects.select_related('category').order_by('-created_at')
    return render(request, 'dashboard/products/list.html', {'products': products})


@staff_required
def product_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price = request.POST.get('discount_price') or None
        stock = request.POST.get('stock')
        category_id = request.POST.get('category')
        is_active = request.POST.get('is_active') == 'on'
        
        category = get_object_or_404(Category, id=category_id)
        
        Product.objects.create(
            name=name,
            slug=slug,
            description=description,
            price=price,
            discount_price=discount_price,
            stock=stock,
            category=category,
            is_active=is_active
        )
        
        messages.success(request, 'Product added successfully!')
        return redirect('dashboard:product_list')
    
    categories = Category.objects.all()
    return render(request, 'dashboard/products/form.html', {'categories': categories, 'product': None})


@staff_required
def product_edit(request, id):
    product = get_object_or_404(Product, id=id)
    
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.slug = request.POST.get('slug')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock')
        product.category = get_object_or_404(Category, id=request.POST.get('category'))
        product.is_active = request.POST.get('is_active') == 'on'
        product.save()
        
        messages.success(request, 'Product updated successfully!')
        return redirect('dashboard:product_list')
    
    categories = Category.objects.all()
    return render(request, 'dashboard/products/form.html', {'categories': categories, 'product': product})


@staff_required
def product_delete(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('dashboard:product_list')


@require_POST
@staff_required
def product_toggle(request, id):
    product = get_object_or_404(Product, id=id)
    product.is_active = not product.is_active
    product.save()
    return JsonResponse({'success': True, 'is_active': product.is_active})


@staff_required
def order_list(request):
    orders = Order.objects.select_related('user').order_by('-created_at')
    return render(request, 'dashboard/orders/list.html', {'orders': orders})


@staff_required
def order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    return render(request, 'dashboard/orders/detail.html', {'order': order})


@require_POST
@staff_required
def order_status(request, id):
    order = get_object_or_404(Order, id=id)
    status = request.POST.get('status')
    if status in ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']:
        order.status = status
        order.save()
        return JsonResponse({'success': True, 'status': status})
    return JsonResponse({'success': False})


@staff_required
def user_list(request):
    users = CustomUser.objects.order_by('-date_joined')
    return render(request, 'dashboard/users/list.html', {'users': users})


@staff_required
def user_detail(request, id):
    user = get_object_or_404(CustomUser, id=id)
    orders = user.orders.order_by('-created_at')
    return render(request, 'dashboard/users/detail.html', {'user': user, 'orders': orders})


@staff_required
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('products')).order_by('name')
    return render(request, 'dashboard/categories/list.html', {'categories': categories})


@staff_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        
        Category.objects.create(name=name, slug=slug)
        messages.success(request, 'Category added successfully!')
        return redirect('dashboard:category_list')
    
    return render(request, 'dashboard/categories/form.html', {'category': None})


@staff_required
def category_edit(request, id):
    category = get_object_or_404(Category, id=id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        category.save()
        messages.success(request, 'Category updated successfully!')
        return redirect('dashboard:category_list')
    
    return render(request, 'dashboard/categories/form.html', {'category': category})


@staff_required
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('dashboard:category_list')


@staff_required
def coupon_list(request):
    coupons = Coupon.objects.order_by('-expiry_date')
    return render(request, 'dashboard/coupons/list.html', {'coupons': coupons})


@staff_required
def coupon_add(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        discount_percent = request.POST.get('discount_percent')
        is_active = request.POST.get('is_active') == 'on'
        expiry_date = request.POST.get('expiry_date')
        
        Coupon.objects.create(
            code=code,
            discount_percent=discount_percent,
            is_active=is_active,
            expiry_date=expiry_date
        )
        messages.success(request, 'Coupon added successfully!')
        return redirect('dashboard:coupon_list')
    
    return render(request, 'dashboard/coupons/form.html', {'coupon': None})


@staff_required
def coupon_edit(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    
    if request.method == 'POST':
        coupon.code = request.POST.get('code')
        coupon.discount_percent = request.POST.get('discount_percent')
        coupon.is_active = request.POST.get('is_active') == 'on'
        coupon.expiry_date = request.POST.get('expiry_date')
        coupon.save()
        messages.success(request, 'Coupon updated successfully!')
        return redirect('dashboard:coupon_list')
    
    return render(request, 'dashboard/coupons/form.html', {'coupon': coupon})


@staff_required
def coupon_delete(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    coupon.delete()
    messages.success(request, 'Coupon deleted successfully!')
    return redirect('dashboard:coupon_list')


@require_POST
@staff_required
def coupon_toggle(request, id):
    coupon = get_object_or_404(Coupon, id=id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    return JsonResponse({'success': True, 'is_active': coupon.is_active})


@staff_required
def revenue_stats(request):
    from django.db.models.functions import TruncDate
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    revenue_data = Order.objects.filter(
        status='DELIVERED',
        created_at__gte=thirty_days_ago
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        total=Sum('total_price')
    ).order_by('date')
    
    data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in revenue_data if item['date']],
        'values': [float(item['total']) for item in revenue_data if item['date']]
    }
    
    return JsonResponse(data)
