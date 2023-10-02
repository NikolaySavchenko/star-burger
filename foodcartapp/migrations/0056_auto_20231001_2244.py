# Generated by Django 3.2.15 on 2023-10-01 19:44

from django.db import migrations

from restaurateur.views import fetch_coordinates


def geolocation(apps, schema_editor):
    orders = apps.get_model('foodcartapp', 'Order')
    locations = apps.get_model('foodcartapp', 'Geolocation')
    orders_set = orders.objects.all()
    locations_set = locations.objects.all()
    for order in orders_set:
        if not locations_set.filter(address=order.address):
            coordinates = fetch_coordinates(order.address)
            if coordinates:
                locations.objects.create(
                    address=order.address,
                    longitude=coordinates[0],
                    latitude=coordinates[1]
                )


class Migration(migrations.Migration):
    dependencies = [
        ('foodcartapp', '0055_geolocation'),
    ]

    operations = [
        migrations.RunPython(geolocation),
    ]
