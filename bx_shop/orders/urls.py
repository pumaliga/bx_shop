from django.urls import path
from .views import OrderCreateView, get_nova_poshta_warehouses, search_nova_poshta_streets, validate_city_for_courier


app_name = 'orders'

urlpatterns = [
    path('create/', OrderCreateView.as_view(), name='order_create'),
    path('get-nova-poshta-warehouses/', get_nova_poshta_warehouses, name='get_nova_poshta_warehouses'),
    path('validate-city/', validate_city_for_courier, name='validate_city_for_courier'),
    path('get-search-streets/', search_nova_poshta_streets, name='search_nova_poshta_streets'),
]
