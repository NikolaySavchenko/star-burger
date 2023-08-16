# Generated by Django 3.2.15 on 2023-08-14 18:56

from django.db import migrations


def get_costs(apps, schema_editor):
    order_details_model = apps.get_model('foodcartapp', 'OrderDetails')
    order_details = order_details_model.objects.all()
    for order_detail in order_details:
        order_detail.cost = order_detail.product.price * order_detail.quantity
        order_detail.save()

class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0043_orderdetails_cost'),
    ]

    operations = [
        migrations.RunPython(get_costs)
    ]
