# Generated by Django 3.2.15 on 2023-09-26 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0051_order_restaurant'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='coordinates',
            field=models.CharField(blank=True, max_length=100, verbose_name='Долгота, Ширина'),
        ),
    ]