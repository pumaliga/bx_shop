from django.views.generic.edit import FormView
from django.shortcuts import redirect
from django.contrib import messages
from .admin_forms import DiscountForm
from .models import Product


class ApplyDiscountView(FormView):
    template_name = 'admin/apply_discount.html'
    form_class = DiscountForm

    def dispatch(self, request, *args, **kwargs):
        # Grab selected product IDs from either GET or POST
        self.ids = request.GET.get('ids', '') if request.method == 'GET' else request.POST.get('_selected_action', '')
        self.ids = self.ids.split(',') if self.ids else []
        self.products = Product.objects.filter(pk__in=self.ids)
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {'_selected_action': self.ids}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'products': self.products,
            'title': 'Apply Discount to Selected Products'
        })
        return context

    def form_valid(self, form):
        percentage = form.cleaned_data['percentage']
        for product in self.products:
            product.apply_discount(percentage)
        messages.success(self.request, f"Applied {percentage}% discount to {self.products.count()} products.")
        return redirect('..')
