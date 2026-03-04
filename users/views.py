from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .forms import CustomUserCreationForm, ProfileForm
from .models import UserProfile
from orders.models import Order
from products.models import Product


def register(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('users:profile')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')


@login_required
def profile(request):
    user = request.user
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    return render(request, 'users/profile.html', {
        'user': user,
        'recent_orders': recent_orders
    })


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'users/orders.html', {'orders': user_orders})


@login_required
def wishlist(request):
    try:
        profile = request.user.profile
        products = profile.wishlist.all()
    except UserProfile.DoesNotExist:
        products = []
    return render(request, 'users/wishlist.html', {'products': products})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if product in profile.wishlist.all():
        profile.wishlist.remove(product)
        in_wishlist = False
    else:
        profile.wishlist.add(product)
        in_wishlist = True
    
    return JsonResponse({'in_wishlist': in_wishlist})
