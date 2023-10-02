from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from restaurateur.views import fetch_coordinates
from .models import Product, Order, OrderDetails, Geolocation


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderDetails
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']


class OrderDBSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address']

@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order_specification = serializer.validated_data

    order_db = Order.objects.create(
        firstname=order_specification['firstname'],
        lastname=order_specification['lastname'],
        phonenumber=order_specification['phonenumber'],
        address=order_specification['address']
    )

    if not Geolocation.objects.filter(address=order_specification['address']):
        coordinates = fetch_coordinates(order_specification['address'])
        if coordinates:
            Geolocation.objects.create(
                address = order_specification['address'],
                longitude = coordinates[0],
                latitude = coordinates[1]
            )

    all_products = Product.objects.all()

    for product in order_specification['products']:
        OrderDetails.objects.create(
            order=order_db,
            product=all_products.get(id=product['product'].id),
            quantity=product['quantity'],
            cost=all_products.get(id=product['product'].id).price * product['quantity']
        )

    order_response = {
        'id': order_db.id,
        'firstname': order_specification['firstname'],
        'lastname': order_specification['lastname'],
        'phonenumber': order_specification['phonenumber'],
        'address': order_specification['address']
    }

    serializer_response = OrderDBSerializer(data=order_response)
    serializer_response.is_valid(raise_exception=True)

    return Response(order_response)
