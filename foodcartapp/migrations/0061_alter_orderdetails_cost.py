# Generated by Django 3.2.15 on 2023-11-10 19:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_alter_orderdetails_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='cost',
            field=models.DecimalField(decimal_places=2, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
    ]
