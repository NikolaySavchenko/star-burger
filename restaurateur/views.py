import requests
from django import forms
from django.conf import settings
from django.db import transaction
from django.db.models import Case, Value, When, IntegerField
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from environs import Env
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order, OrderDetails, RestaurantMenuItem, Geolocation


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


def fetch_coordinates(address):
    apikey = settings.APIKEY
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def orders_for_manager(order, orders_details, current_url, restaurants_menu, geolocations):
    order_details = get_orders_details(order, orders_details, restaurants_menu, geolocations)
    if order.restaurant:
        restaurant = f'Готовится в: {order.restaurant.name}'
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


def get_orders_details(order, orders_details, restaurants_menu, geolocations):
    order_cost = 0
    order_restaurants = set()
    order_details = set()
    client_coordinates = tuple()

    for geolocation in geolocations:
        if geolocation.address == order.address:
            client_coordinates = (geolocation.longitude, geolocation.latitude)

    if not client_coordinates:
        try:
            client_coordinates = fetch_coordinates(order.address)
            Geolocation.objects.create(
                address=order.address,
                longitude=client_coordinates[0],
                latitude=client_coordinates[1]
            )
        except:
            client_coordinates = None

    for item in orders_details:
        if item.order == order:
            order_details.add(item)

    for item in order_details:
        order_cost += item.cost
        product_restaurants = set()
        for restaurant_menu in restaurants_menu:
            if restaurant_menu.product == item.product and restaurant_menu.availability:
                product_restaurants.add(restaurant_menu.restaurant)

        if not order_restaurants:
            order_restaurants = product_restaurants
        else:
            order_restaurants = order_restaurants.intersection(product_restaurants)

    restaurants_name = {}
    for restaurant in order_restaurants:
        if client_coordinates != None:
            distance_to_restaurant = format(
                distance.distance(
                    (client_coordinates[1], client_coordinates[0]),
                    (restaurant.latitude, restaurant.longitude)
                ).km, '.2f'
            )
            restaurants_name[restaurant.name] = distance_to_restaurant
        else:
            restaurants_name[restaurant.name] = 'Расстояние неизвестно'

    return {
        'order_cost': order_cost,
        'restaurants': sorted(restaurants_name.items(), key=lambda x: x[1])
    }


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
    restaurants_menu = RestaurantMenuItem.objects.all().prefetch_related('restaurant').select_related('product')
    geolocations = Geolocation.objects.all()

    context = {
        'orders': [orders_for_manager(order, orders_details, current_url, restaurants_menu, geolocations) for order in
                   orders]
    }

    return render(request, template_name='order_items.html', context=context)
