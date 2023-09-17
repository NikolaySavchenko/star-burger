from django import forms
from django.db import transaction
from django.db.models import Case, Value, When, IntegerField
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Product, Restaurant, Order, OrderDetails, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def orders_for_manager(order, orders_details, current_url, restaurants_menu):
    order_details = get_orders_details(order, orders_details, restaurants_menu)
    if order.restaurant:
        restaurant = f'Готовиться в: {order.restaurant.name}'
    else:
        restaurant = f'Может быть приготовлено в: {order_details["restaurants"]}'
    return {
        'id': order.id,
        'status': order.get_status_display(),
        'payment_method': order.get_payment_method_display(),
        'cost': order_details['order_cost'],
        'name': order.firstname,
        'phonenumber': order.phonenumber,
        'address': order.address,
        'comment': order.comment,
        'restaurant': restaurant,
        'edit_link': reverse('admin:foodcartapp_order_change', args=(order.id,)),
        'currentUrl': current_url
    }


def get_orders_details(order, orders_details, restaurants_menu):
    order_cost = 0
    order_restaurants = set()
    order_details = set()

    for item in orders_details:
        if item.order == order:
            order_details.add(item)

    for item in order_details:
        order_cost += item.cost
        product_restaurants = set()
        for restaurant_menu in restaurants_menu:
            if restaurant_menu.product == item.product and restaurant_menu.availability:
                product_restaurants.add(restaurant_menu)
        restaurants_name = set()
        for restaurant in product_restaurants:
            restaurants_name.add(restaurant.restaurant.name)
        if not order_restaurants:
            order_restaurants = restaurants_name
        else:
            order_restaurants = order_restaurants.intersection(restaurants_name)

    return {'order_cost': order_cost, 'restaurants': order_restaurants}


@transaction.atomic
@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    current_url = request.path
    orders = Order.objects.exclude(status='C').prefetch_related('restaurant').annotate(
        status_sort=Case(
            When(status='N', then=Value(1)),
            When(status='R', then=Value(2)),
            When(status='D', then=Value(3)),
            When(status='C', then=Value(4)),
            output_field=IntegerField(),
        )
    ).order_by('status_sort', 'id')
    orders_details = OrderDetails.objects.all().prefetch_related('order').select_related('product')
    restaurants_menu = RestaurantMenuItem.objects.all().prefetch_related('product').select_related('restaurant')

    context = {
        'orders': [orders_for_manager(order, orders_details, current_url, restaurants_menu) for order in orders]
    }

    return render(request, template_name='order_items.html', context=context)
