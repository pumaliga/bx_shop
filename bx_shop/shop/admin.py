from .models import Category, Product, Size, ProductImage
from django.shortcuts import redirect
from django.urls import path
from django.contrib import admin
from django.contrib.admin.helpers import ACTION_CHECKBOX_NAME

from .admin_views import ApplyDiscountView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # how many blank image forms to show
    max_num = 10  # optional limit


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'available', 'material_from',
                    'material_inside', 'material_sole', 'color', 'created', 'updated',
                    'price', 'discount_price', 'get_final_price', 'is_discounted']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'discount_price', 'available']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['available_sizes']
    inlines = [ProductImageInline]
    actions = ['apply_discount', 'remove_discounts']

    @admin.action(description="Apply custom discount %%")
    def apply_discount(self, request, queryset):
        selected = request.POST.getlist(ACTION_CHECKBOX_NAME)
        return redirect(f'apply-discount/?ids={",".join(selected)}')

    @admin.action(description="Remove discounts from selected products")
    def remove_discounts(self, request, queryset):
        updated = 0
        for product in queryset:
            if product.is_discounted():
                product.remove_discount()
                updated += 1
        self.message_user(request, f"Removed discounts from {updated} product(s).")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('apply-discount/', self.admin_site.admin_view(ApplyDiscountView.as_view()), name='apply_discount'),
        ]
        return custom_urls + urls


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['size']
