# Generated by Django 3.2.15 on 2023-07-12 19:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0040_auto_20230629_2232'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='first_name',
            new_name='firstname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='last_name',
            new_name='lastname',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='phone',
            new_name='phonenumber',
        ),
        migrations.RenameField(
            model_name='orderdetails',
            old_name='count',
            new_name='quantity',
        ),
    ]
