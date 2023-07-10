from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
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


@api_view(['POST'])
def register_order(request):
    order_specification = request.data

    if not isinstance(order_specification['firstname'], str):
        return Response(f'Введите корректные данные в поле Имя')
    elif not isinstance(order_specification['lastname'], str):
        return Response(f'Введите корректные данные в поле Фамилия')
    elif not isinstance(order_specification['phonenumber'], str):
        return Response(f'Введите корректные данные в поле Телефон')
    elif not isinstance(order_specification['address'], str):
        return Response(f'Введите корректные данные в поле Адрес')
    elif not order_specification['products']:
        return Response(f'Введите поле Продукты')
    elif not isinstance(order_specification['products'], list) or \
        len(order_specification['products']) < 1:
        return Response(f'Введите данные в поле Продукты')

    order_db, created = Order.objects.get_or_create(
        first_name=order_specification['firstname'],
        last_name=order_specification['lastname'],
        phone=order_specification['phonenumber'],
        address=order_specification['address']
    )
    all_products = Product.objects.all()

    for product in order_specification['products']:
        if not product['product'] or not product['quantity']:
            return Response(f'Введите поля Продукт и Количество')
        elif not isinstance(product['product'], int) or not isinstance(product['quantity'], int):
            return Response(f'Поля Продукт и Количество должны быть целым числом')
        elif product['product'] < 1 or product['quantity'] < 1:
            return Response(f'Поля Продукт и Количество должны быть положительным целым числом')
        OrderDetails.objects.get_or_create(
            order=order_db,
            product=all_products.get(id=product['product']),
            count=product['quantity']
        )

    return Response({})
