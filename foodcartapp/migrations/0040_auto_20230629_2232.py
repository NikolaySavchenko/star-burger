# Generated by Django 3.2.15 on 2023-06-29 19:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0039_order_details'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Order_details',
            new_name='OrderDetails',
        ),
        migrations.AlterModelOptions(
            name='orderdetails',
            options={'verbose_name': 'Состав заказа', 'verbose_name_plural': 'Состав заказов'},
        ),
    ]
