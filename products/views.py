from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Review, ProductImage
from orders.models import OrderItem


def home(request):
    featured_products = Product.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')[:8]
    categories = Category.objects.all()
    bestsellers = Product.objects.filter(is_active=True).annotate(
        order_count=Count('orderitem')
    ).order_by('-order_count')[:5]
    
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'categories': categories,
        'bestsellers': bestsellers,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating')
    )
    categories = Category.objects.all()
    
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    else:
        products = products.order_by('-created_at')
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    product_images = product.images.all()
    
    return render(request, 'products/detail.html', {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'related_products': related_products,
        'product_images': product_images,
    })


def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(is_active=True).annotate(
        avg_rating=Avg('reviews__rating')
    )
    
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/search.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'query': query,
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True).annotate(
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')
    categories = Category.objects.all()
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': categories,
        'current_category': category,
    })


@login_required
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, 'Review submitted successfully!')
        else:
            messages.error(request, 'Please provide both rating and comment.')
    
    return redirect('products:product_detail', slug=product.slug)
