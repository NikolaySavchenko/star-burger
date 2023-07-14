from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Product, Order, OrderDetails


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


def order_validate(data):
    errors = []
    if 'firstname' not in data:
        errors.append('Введите поле Имя')
    elif not isinstance(data['firstname'], str) or \
        len(data['firstname']) < 1:
        errors.append('Введите корректные данные в поле Имя')
    if 'lastname' not in data:
        errors.append('Введите поле Фамилия')
    elif not isinstance(data['lastname'], str) or \
        len(data['lastname']) < 1:
        errors.append('Введите корректные данные в поле Фамилия')
    if 'phonenumber' not in data:
        errors.append('Введите поле Телефон')
    elif not isinstance(data['phonenumber'], str)or \
        len(data['phonenumber']) < 1:
        errors.append('Введите корректные данные в поле Телефон')
    elif not PhoneNumber.from_string(data['phonenumber']).is_valid():
        errors.append('Введите корректные данные в поле Телефон')
    elif len(data['phonenumber']) < 1:
        errors.append('Введите данные в поле Телефон')
    if 'address' not in data:
        errors.append('Введите поле Адрес')
    elif not isinstance(data['address'], str) or \
        len(data['address']) < 1:
        errors.append('Введите корректные данные в поле Адрес')
    if 'products' not in data:
        errors.append('Введите поле Продукты')
    elif not isinstance(data['products'], list) or \
        len(data['products']) < 1:
        errors.append('Введите данные в поле Продукты')

    if errors:
        raise ValidationError(errors)


def product_validate(data, ids):
    errors = []
    if 'product' not in data:
        errors.append('Введите поля Продукт')
    elif not isinstance(data['product'], int):
        errors.append('Поле Продукт должно содержать целое число')
    elif data['product'] not in ids:
        errors.append('Поле Продукт должны содержать существующий ID продукта')
    if 'quantity' not in data:
        errors.append('Введите поля Количество')
    elif not isinstance(data['quantity'], int):
        errors.append('Поле Количество должно содержать целое число')
    elif data['quantity'] < 1:
        errors.append('Поле Количество должно содержать положительное целое число')

    if errors:
        raise ValidationError(errors)


@api_view(['POST'])
def register_order(request):
    order_specification = request.data
    order_validate(order_specification)

    order_db, created = Order.objects.get_or_create(
        firstname=order_specification['firstname'],
        lastname=order_specification['lastname'],
        phonenumber=order_specification['phonenumber'],
        address=order_specification['address']
    )
    all_products = Product.objects.all()
    ids = []
    for product in all_products:
        ids.append(product.id)

    for product in order_specification['products']:
        product_validate(product, ids)
        OrderDetails.objects.get_or_create(
            order=order_db,
            product=all_products.get(id=product['product']),
            quantity=product['quantity']
        )

    return Response({})
