from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review


class ProductInline(admin.TabularInline):
    model = Product
    extra = 1
    fields = ['name', 'slug', 'price', 'discount_price', 'stock', 'is_active', 'image']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'name', 'price', 'discount_price', 'stock', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('thumbnail_preview',)
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;">', obj.image.url)
        return '-'
    thumbnail.short_description = 'Image'
    
    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" style="object-fit: cover;">', obj.image.url)
        return '-'
    thumbnail_preview.short_description = 'Image Preview'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['thumbnail', 'product', 'created_at']
    
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;">', obj.image.url)
        return '-'
    thumbnail.short_description = 'Image'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
