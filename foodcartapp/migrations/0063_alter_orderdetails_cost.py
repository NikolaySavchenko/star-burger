# Generated by Django 3.2.15 on 2023-11-21 19:27

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0062_auto_20231118_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetails',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Стоимость'),
        ),
    ]
