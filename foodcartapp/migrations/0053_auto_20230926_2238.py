# Generated by Django 3.2.15 on 2023-09-26 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_restaurant_coordinates'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='coordinates',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='latitude',
            field=models.FloatField(default=1.0, verbose_name='Широта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='restaurant',
            name='longitude',
            field=models.FloatField(default=1.0, verbose_name='Долгота'),
            preserve_default=False,
        ),
    ]
