# Generated by Django 3.2.15 on 2023-09-02 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20230902_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='call_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время звонка'),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Время доставки'),
        ),
        migrations.AlterField(
            model_name='order',
            name='firstname',
            field=models.CharField(max_length=20, verbose_name='Имя клиента'),
        ),
        migrations.AlterField(
            model_name='order',
            name='lastname',
            field=models.CharField(max_length=20, verbose_name='Фамилия клиента'),
        ),
    ]