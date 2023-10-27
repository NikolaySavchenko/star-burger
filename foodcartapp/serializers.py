from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderDetails, Order


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
