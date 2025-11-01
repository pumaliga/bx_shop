from django.db import models
from shop.models import Product


DELIVERY_PROVIDERS = [
    ('nova_poshta', 'Nova Poshta'),
    ('ukrposhta', 'Ukrposhta'),
]

DELIVERY_TYPES = [
    ('branch', 'Branch Pickup'),
    ('courier', 'Courier Delivery'),
]

ORDER_STATUS_CHOICES = [
    ('new', 'New'),
    ('processing', 'Processing'),
    ('complete', 'Complete'),
    ('canceled', 'Canceled'),
]


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    city = models.CharField(max_length=100)
    delivery_provider = models.CharField(max_length=30, choices=DELIVERY_PROVIDERS, default='nova_poshta')
    delivery_type = models.CharField(max_length=30, choices=DELIVERY_TYPES, default='branch')
    # For courier delivery
    street = models.CharField(max_length=255, blank=True, null=True)
    house_number = models.CharField(max_length=10, blank=True, null=True)  # TODO int
    flat_number = models.CharField(max_length=10, blank=True, null=True)
    # For post office delivery
    warehouse_description = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='new')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return 'Order {}'.format(self.pk)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.pk)

    def get_cost(self):
        return self.price * self.quantity
