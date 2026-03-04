from decimal import Decimal
from django.utils import timezone
from .models import Cart, CartItem, Coupon


def get_cart(request):
    """Get or create cart for user or session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        if request.session.session_key is None:
            request.session.create()
        session_key = request.session.session_key
        
        session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
        if session_cart:
            merge_carts(session_key, request.user)
        
        return cart
    else:
        session_key = request.session.session_key
        if session_key is None:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(
            session_key=session_key,
            user__isnull=True,
            defaults={'session_key': session_key}
        )
        return cart


def merge_carts(session_key, user):
    """Merge session cart into user's DB cart"""
    session_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
    if not session_cart:
        return
    
    user_cart, _ = Cart.objects.get_or_create(user=user)
    
    for item in session_cart.items.all():
        existing_item = user_cart.items.filter(product=item.product).first()
        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.save()
        else:
            CartItem.objects.create(
                cart=user_cart,
                product=item.product,
                quantity=item.quantity
            )
    
    session_cart.delete()


def get_cart_items(request):
    """Get all cart items with calculated prices"""
    cart = get_cart(request)
    items = []
    
    for item in cart.items.all():
        items.append({
            'id': item.id,
            'product': item.product,
            'quantity': item.quantity,
            'price': item.product.final_price,
            'total': item.product.final_price * item.quantity,
        })
    
    return items


def get_cart_total(request):
    """Calculate cart subtotal"""
    items = get_cart_items(request)
    subtotal = sum(item['total'] for item in items)
    return subtotal


def get_cart_count(request):
    """Get total number of items in cart"""
    cart = get_cart(request)
    return sum(item.quantity for item in cart.items.all())


def apply_coupon_code(request, code):
    """Apply coupon code and return discount amount"""
    try:
        coupon = Coupon.objects.get(code=code.upper(), is_active=True)
        if coupon.expiry_date < timezone.now():
            return {'success': False, 'message': 'Coupon has expired'}
        
        subtotal = get_cart_total(request)
        discount = (subtotal * coupon.discount_percent) / Decimal('100')
        
        return {
            'success': True,
            'discount': discount,
            'new_total': subtotal - discount,
            'message': f'Coupon applied! {coupon.discount_percent}% off'
        }
    except Coupon.DoesNotExist:
        return {'success': False, 'message': 'Invalid coupon code'}


def clear_cart(request):
    """Clear all items from cart"""
    cart = get_cart(request)
    cart.items.all().delete()
