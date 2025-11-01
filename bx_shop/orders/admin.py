from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class BaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'postal_code', 'city', 'status', 'created', 'updated']
    list_filter = ['created', 'updated']
    list_editable = ['status']
    inlines = [OrderItemInline]


class NewOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='new')


class ProcessingOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='processing')


class CompleteOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='complete')


class CanceledOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status='canceled')


class NewOrderProxy(Order):
    class Meta:
        proxy = True
        verbose_name = 'New Order'
        verbose_name_plural = 'New Orders'


class ProcessingOrderProxy(Order):
    class Meta:
        proxy = True
        verbose_name = 'Processing Order'
        verbose_name_plural = 'Processing Orders'


class CompleteOrderProxy(Order):
    class Meta:
        proxy = True
        verbose_name = 'Complete Order'
        verbose_name_plural = 'Complete Orders'


class CanceledOrderProxy(Order):
    class Meta:
        proxy = True
        verbose_name = 'Canceled Order'
        verbose_name_plural = 'Canceled Orders'


admin.site.register(NewOrderProxy, NewOrderAdmin)
admin.site.register(ProcessingOrderProxy, ProcessingOrderAdmin)
admin.site.register(CompleteOrderProxy, CompleteOrderAdmin)
admin.site.register(CanceledOrderProxy, CanceledOrderAdmin)
