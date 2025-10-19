import re
from django.views.generic.edit import FormView
from django.shortcuts import render
from django.http import JsonResponse

from cart.cart import Cart
from .forms import OrderCreateForm
from .models import OrderItem
from .services.newposh import get_warehouses_by_city, get_streets_by_city_ref, get_city_ref_by_name


class OrderCreateView(FormView):
    template_name = 'orders/create.html'
    form_class = OrderCreateForm

    def form_valid(self, form):
        cart = Cart(self.request)
        order = form.save()
        # Create OrderItem entries for each item in the cart
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                price=item['price'],
                quantity=item['quantity']
            )

        # Clear the cart after saving the order
        cart.clear()
        return render(self.request, 'orders/created.html', {'order': order})


def is_valid_city_format(query):
    """
    Validate city and street format: at least 4 chars, only letters, spaces, apostrophes, and hyphens
    """
    if len(query) < 4:
        return False
    return bool(re.match(r"^[a-zA-Zа-яА-ЯіІїЇєЄ'\s-]+$", query))


def get_nova_poshta_warehouses(request):
    city = request.GET.get('city', '').strip()

    if not city:
        return JsonResponse({'error': 'City is required'})

    # Validate city format before making API call
    if not is_valid_city_format(city):
        return JsonResponse({'error': 'Please enter a valid city name'})

    data = get_warehouses_by_city(city)
    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data)

    return JsonResponse(data, safe=False)


def validate_city_for_courier(request):
    """
    Validate if city is valid for Nova Poshta courier delivery.
    Stores city_ref in session if valid.
    """
    city = request.GET.get('city', '').strip()
    if not city:
        return JsonResponse({'error': 'City is required'})

    # Validate city format before making API call
    if not is_valid_city_format(city):
        return JsonResponse({'error': 'Please enter a valid city name'})

    city_ref = get_city_ref_by_name(city)
    if isinstance(city_ref, dict) and 'error' in city_ref:
        return JsonResponse(city_ref)

    # Store validated city_ref in session
    request.session['nova_poshta_city_ref'] = city_ref
    request.session['nova_poshta_city_name'] = city
    
    return JsonResponse({'success': True, 'city': city})


def search_nova_poshta_streets(request):
    # Get city_ref from session (must be validated first)
    city_ref = request.session.get('nova_poshta_city_ref')
    if not city_ref:
        return JsonResponse({'error': 'City must be validated first. Please select a valid city.'})
    
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'error': 'Street name is required'})

    # Search for streets using the validated city reference from session
    data = get_streets_by_city_ref(city_ref, query)
    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data)

    suggestions = [
        {"label": street["Description"], "ref": street["Ref"]}
        for street in data
    ]

    return JsonResponse(suggestions, safe=False)
