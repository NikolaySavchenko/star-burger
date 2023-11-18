# Generated by Django 3.2.15 on 2023-11-05 18:31

import django.core.validators
from django.db import migrations, models
import foodcartapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0058_auto_20231027_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=foodcartapp.models.OrderDetails.cost_value, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
    ]