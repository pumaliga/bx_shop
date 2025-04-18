from decimal import Decimal
from django.conf import settings
from shop.models import Product, Size


class Cart(object):
    def __init__(self, request):
        """Init cart instance"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)

        if not cart:
            # Save empty cart in session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, size, quantity=1, update_quantity=False):
        """Add products to cart or update its quantity, including size"""

        if not size:
            raise ValueError("Size must be provided when adding an item to the cart.")

        # Use a composite key of product ID and size ID to make unique variants
        cart_key = f"{product.id}-{size}"

        if cart_key not in self.cart:
            self.cart[cart_key] = {
                'quantity': 0,
                'price': str(product.price)
            }

        if update_quantity:
            self.cart[cart_key]['quantity'] = quantity
        else:
            self.cart[cart_key]['quantity'] += quantity
        self.save()

    def save(self):
        # Mark session as updated
        self.session.modified = True

    def remove(self, product, size):
        """Delete product from cart"""
        key = f"{product.id}-{size}"
        if key in self.cart:
            del self.cart[key]
            self.save()

    def __iter__(self):
        """Go through the cart of products and get corresponding Product objects"""
        cart = self.cart.copy()
        product_ids = []  # list allows duplicate product IDs
        size_ids = set()  # set ensures each size ID is only included once

        for key in cart:
            product_id, size_id = key.split('-')
            product_ids.append(product_id)
            size_ids.add(size_id)

        products = Product.objects.filter(id__in=product_ids)
        sizes = Size.objects.filter(id__in=size_ids)

        product_map = {str(product.id): product for product in products}
        size_map = {str(size.id): size for size in sizes}

        for key, item in cart.items():
            product_id, size_id = key.split('-')
            item['product'] = product_map[product_id]
            item['size'] = size_map.get(size_id)
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """Return total quantity of products in cart"""
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(
            Decimal(item['price']) * item['quantity']
            for item in self.cart.values())

    def clear(self):
        # Clean up cart
        del self.session[settings.CART_SESSION_ID]
        self.save()

