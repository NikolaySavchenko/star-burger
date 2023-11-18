# Generated by Django 3.2.15 on 2023-11-18 15:35

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0061_alter_orderdetails_cost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='restaurant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_preparing', to='foodcartapp.restaurant', verbose_name='Готовится в ресторане'),
        ),
        migrations.AlterField(
            model_name='orderdetails',
            name='quantity',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(99), django.core.validators.MinValueValidator(1)], verbose_name='Количество'),
        ),
    ]
