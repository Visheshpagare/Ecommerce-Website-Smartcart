from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_list_or_404
from decimal import Decimal
from products.models import Product
from .models import Order, OrderItem, CartItem
from .cart_utils import get_cart, get_cart_items, get_cart_total, get_cart_count, apply_coupon_code, clear_cart


def cart(request):
    items = get_cart_items(request)
    subtotal = get_cart_total(request)
    
    coupon_discount = request.session.get('coupon_discount', 0)
    total = subtotal - Decimal(str(coupon_discount))
    
    return render(request, 'orders/cart.html', {
        'items': items,
        'subtotal': subtotal,
        'coupon_discount': coupon_discount,
        'total': total,
    })


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    quantity = int(request.POST.get('quantity', 1))
    
    cart = get_cart(request)
    
    existing_item = cart.items.filter(product=product).first()
    if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
        message = 'Cart updated successfully'
    else:
        CartItem.objects.create(cart=cart, product=product, quantity=quantity)
        message = 'Added to cart successfully'
    
    cart_count = get_cart_count(request)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'message': message
        })
    
    messages.success(request, message)
    return redirect('orders:cart')


@require_POST
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    
    cart_count = get_cart_count(request)
    subtotal = get_cart_total(request)
    coupon_discount = request.session.get('coupon_discount', 0)
    total = subtotal - Decimal(str(coupon_discount))
    
    item_total = item.quantity * item.product.final_price if item.quantity > 0 else 0
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'item_total': str(item_total) if item.quantity > 0 else '0',
            'cart_total': str(total),
            'cart_count': cart_count
        })
    
    return redirect('orders:cart')


@require_POST
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    
    cart_count = get_cart_count(request)
    subtotal = get_cart_total(request)
    coupon_discount = request.session.get('coupon_discount', 0)
    total = subtotal - Decimal(str(coupon_discount))
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': str(total),
            'cart_count': cart_count
        })
    
    messages.success(request, 'Item removed from cart')
    return redirect('orders:cart')


@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '')
    result = apply_coupon_code(request, code)
    
    if result['success']:
        request.session['coupon_code'] = code.upper()
        request.session['coupon_discount'] = str(result['discount'])
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(result)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('orders:cart')


@login_required
def checkout(request):
    cart_items = get_cart_items(request)
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('orders:cart')
    
    subtotal = get_cart_total(request)
    coupon_discount = request.session.get('coupon_discount', 0)
    total = subtotal - Decimal(str(coupon_discount))
    
    user = request.user
    initial_data = {
        'shipping_address': user.address or '',
    }
    
    return render(request, 'orders/checkout.html', {
        'items': cart_items,
        'subtotal': subtotal,
        'coupon_discount': coupon_discount,
        'total': total,
        'user': user,
    })


@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('orders:checkout')
    
    cart_items = get_cart_items(request)
    if not cart_items:
        messages.error(request, 'Your cart is empty')
        return redirect('orders:cart')
    
    shipping_address = request.POST.get('shipping_address', '')
    if not shipping_address:
        messages.error(request, 'Please provide a shipping address')
        return redirect('orders:checkout')
    
    full_name = request.POST.get('full_name', '')
    email = request.POST.get('email', '')
    
    if full_name:
        name_parts = full_name.split(' ', 1)
        request.user.first_name = name_parts[0]
        request.user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        request.user.save()
    
    if email:
        request.user.email = email
        request.user.save()
    
    subtotal = get_cart_total(request)
    coupon_discount = Decimal(request.session.get('coupon_discount', 0))
    total = subtotal - coupon_discount
    
    order = Order.objects.create(
        user=request.user,
        total_price=total,
        status='PENDING',
        payment_status='PENDING',
        shipping_address=shipping_address
    )
    
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            quantity=item['quantity'],
            price=item['product'].final_price
        )
        
        if item['product'].stock >= item['quantity']:
            item['product'].stock -= item['quantity']
            item['product'].save()
    
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'coupon_discount' in request.session:
        del request.session['coupon_discount']
    
    clear_cart(request)
    
    return redirect('orders:order_confirmation', order_id=order.id)


def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.user.is_authenticated and order.user != request.user:
        return redirect('products:home')
    
    return render(request, 'orders/confirmation.html', {
        'order': order,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/detail.html', {
        'order': order,
    })
