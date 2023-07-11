from django.http import JsonResponse
from django.templatetags.static import static
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework import status
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

    try:
        if not isinstance(order_specification['firstname'], str) or \
            len(order_specification['firstname']) < 1:
            return Response(f'Введите корректные данные в поле Имя',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not isinstance(order_specification['lastname'], str) or \
            len(order_specification['lastname']) < 1:
            return Response(f'Введите корректные данные в поле Фамилия',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not PhoneNumber.from_string(order_specification['phonenumber']).is_valid():
            return Response(f'Введите корректные данные в поле Телефон',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not isinstance(order_specification['address'], str) or \
            len(order_specification['address']) < 1:
            return Response(f'Введите корректные данные в поле Адрес',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not order_specification['products']:
            return Response(f'Введите поле Продукты',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        elif not isinstance(order_specification['products'], list) or \
            len(order_specification['products']) < 1:
            return Response(f'Введите данные в поле Продукты',
                            status=status.HTTP_406_NOT_ACCEPTABLE)
    except:
        return Response(f'Данные введены неверно!',
                        status=status.HTTP_406_NOT_ACCEPTABLE)

    order_db, created = Order.objects.get_or_create(
        first_name=order_specification['firstname'],
        last_name=order_specification['lastname'],
        phone=order_specification['phonenumber'],
        address=order_specification['address']
    )
    all_products = Product.objects.all()
    ids = []
    for product in all_products:
        ids.append(product.id)

    for product in order_specification['products']:
        try:
            if not product['product'] or not product['quantity']:
                return Response(f'Введите поля Продукт и Количество',
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            elif not isinstance(product['product'], int) or not isinstance(product['quantity'], int):
                return Response(f'Поля Продукт и Количество должны быть целым числом',
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            elif product['quantity'] < 1:
                return Response(f'Поле Количество должны быть положительным целым числом',
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            elif product['product'] not in ids:
                return Response(f'Поле Продукт должны содержать существующий ID продукта',
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        except:
            return Response(f'Данные введены неверно!', status=status.HTTP_406_NOT_ACCEPTABLE)

        OrderDetails.objects.get_or_create(
            order=order_db,
            product=all_products.get(id=product['product']),
            count=product['quantity']
        )

    return Response({})
