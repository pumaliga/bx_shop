from django.db import models
from django.urls import reverse
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_list_by_category', args=[self.slug])


class Size(models.Model):
    size = models.CharField(max_length=5, unique=True)

    class Meta:
        ordering = ['size']

    def __str__(self):
        return self.size


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)
    material_from = models.CharField(max_length=200, blank=True)
    material_inside = models.CharField(max_length=200, blank=True)
    material_sole = models.CharField(max_length=200, blank=True)
    color = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available = models.BooleanField(default=True)
    available_sizes = models.ManyToManyField(Size, related_name='products', blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
        indexes = [models.Index(fields=['id', 'slug']),]

    def get_final_price(self):
        """
        Return the price to display, using the discounted price if available.
        Returns:
            Decimal: The final price after applying the discount (if any).
        """
        return self.discount_price if self.discount_price else self.price

    def is_discounted(self):
        """
        Check if the product has an active discount.
        Returns:
            bool: True if the product is discounted, False otherwise.
        """
        return self.discount_price is not None and self.discount_price < self.price

    def apply_discount(self, percentage: Decimal):
        """Apply a discount based on a given percentage (e.g., 20%)."""
        discount_factor = Decimal((100 - percentage) / 100)
        self.discount_price = self.price * discount_factor
        self.save(update_fields=['discount_price'])

    def remove_discount(self):
        """Remove any active discount from the product."""
        self.discount_price = None
        self.save(update_fields=['discount_price'])

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.pk, self.slug])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/%Y/%m/%d/', blank=True, null=True)

    def __str__(self):
        return f"Image for product: {self.product.name}"
