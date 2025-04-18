from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Product
from cart.forms import CartAddProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'
    paginate_by = 6

    def get_queryset(self):
        """Filter products based on availability and category (if provided)."""
        queryset = Product.objects.filter(available=True)
        category_slug = self.kwargs.get('category_slug')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        return queryset

    def get_context_data(self, **kwargs):
        """Add categories and selected category to the context."""
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        context['categories'] = Category.objects.all()
        context['category'] = get_object_or_404(Category, slug=category_slug) if category_slug else None
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        """Display only available products."""
        return Product.objects.filter(available=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        # Passing the product to the form allows the form to access the product's available sizes
        context['cart_product_form'] = CartAddProductForm(product=product)
        return context

    # def get_context_data(self, **kwargs):
    #     """Add cart form to the context."""
    #     context = super().get_context_data(**kwargs)
    #     context['cart_product_form'] = CartAddProductForm()
    #     return context

