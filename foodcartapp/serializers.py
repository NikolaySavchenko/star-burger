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

    def create(self, validation_data):
        order = Order.objects.create(
            firstname=validation_data.get('firstname'),
            lastname=validation_data.get('lastname'),
            phonenumber=validation_data.get('phonenumber'),
            address=validation_data.get('address')
        )
        for product in validation_data.get('products'):
            new_detail = OrderDetails.objects.create(order=order, **product)
            new_detail.cost_value()

        return order
