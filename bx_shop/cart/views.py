from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseBadRequest
from django.views.generic import TemplateView
from django.views import View
from shop.models import Product
from .cart import Cart
from .forms import CartAddProductForm


class CartAddView(View):
    """Handles adding products to the cart."""
    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        form = CartAddProductForm(request.POST, product=product)

        if form.is_valid():
            cd = form.cleaned_data
            size = cd.get('size') or request.POST.get('size')

            if not size:
                return HttpResponseBadRequest("Size is required.")

            cart.add(
                product=product,
                quantity=cd['quantity'],
                update_quantity=cd['update'],
                size=size
            )

            return redirect('cart:cart_detail')

        return HttpResponseBadRequest("Invalid form submission")


class CartRemoveView(View):
    """Removes a product from the cart."""

    def post(self, request, product_id):
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        size = request.POST.get('size')
        # cart.remove(product)
        cart.remove(product, size)

        return redirect('cart:cart_detail')


class CartDetailView(TemplateView):
    """Displays the cart details and allows quantity updates."""
    template_name = 'cart/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart(self.request)

        # Add an update form for each cart item
        for item in cart:
            item['update_quantity_form'] = CartAddProductForm(
                initial={'quantity': item['quantity'], 'update': True}
            )

        context['cart'] = cart
        return context


