# Generated by Django 3.2.15 on 2023-05-08 16:33

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=20, verbose_name='Ваше имя')),
                ('last_name', models.CharField(blank=True, max_length=20, verbose_name='Ваша фамилия')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(db_index=True, max_length=128, region=None, verbose_name='Номер телефона')),
                ('address', models.CharField(max_length=50, verbose_name='Адрес доставки')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
    ]