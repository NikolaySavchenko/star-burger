import json
from django.http import JsonResponse
from django.templatetags.static import static

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


def register_order(request):
    # url = 'http://127.0.0.1:8000/api/order/'

    def order_detail(request):
        try:
            return json.loads(request.body.decode())
        except ValueError:
            return JsonResponse({
                'error': 'Введите корректное значение',
            })

    order_specification = order_detail(request)
    order_db, created = Order.objects.get_or_create(
        first_name=order_specification['firstname'],
        last_name=order_specification['lastname'],
        phone=order_specification['phonenumber'],
        address=order_specification['address']
    )
    all_products = Product.objects.all()
    for product in order_specification['products']:
        OrderDetails.objects.get_or_create(
            order=order_db,
            product=all_products.get(id=product['product']),
            count=product['quantity']
        )

    return JsonResponse({})
