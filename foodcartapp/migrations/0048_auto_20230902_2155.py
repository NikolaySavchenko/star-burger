# Generated by Django 3.2.15 on 2023-09-02 18:55

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0047_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='call_time',
            field=models.DateTimeField(null=True, verbose_name='Время звонка'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_time',
            field=models.DateTimeField(null=True, verbose_name='Время доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='order_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Время получения заказ'),
            preserve_default=False,
        ),
    ]
