from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    longitude = models.CharField('Долгота', max_length=10)
    latitude = models.CharField('Широта', max_length=10)

    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class Order(models.Model):
    STATUS = (
        ('N', 'Новый'),
        ('R', 'Готовится'),
        ('D', 'Доставляется'),
        ('C', 'Завершен'),
    )
    PAYMENT = (
        ('C', 'Наличные'),
        ('E', 'Электронные'),
    )
    firstname = models.CharField(
        'Имя клиента',
        max_length=20
    )
    lastname = models.CharField(
        'Фамилия клиента',
        max_length=20
    )
    phonenumber = PhoneNumberField(
        'Номер телефона',
        db_index=True
    )
    address = models.CharField(
        'Адрес доставки',
        max_length=50
    )
    status = models.CharField(
        'Статус заказа',
        max_length=1,
        choices=STATUS,
        default='N',
        db_index=True
    )
    comment = models.TextField(
        'Комментарий',
        max_length=100,
        blank=True
    )
    order_time = models.DateTimeField(
        'Время получения заказ',
        auto_now_add=True
    )
    call_time = models.DateTimeField(
        'Время звонка',
        null=True,
        blank=True
    )
    delivery_time = models.DateTimeField(
        'Время доставки',
        null=True,
        blank=True
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=1,
        choices=PAYMENT,
        default='C',
        db_index=True
    )
    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='Готовится в ресторане',
        related_name='orders_preparing',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.firstname


class OrderDetails(models.Model):
    order = models.ForeignKey(
        Order,
        verbose_name='Заказ',
        related_name='order_consist',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Продукт',
        related_name='products',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        validators=[MaxValueValidator(99), MinValueValidator(1)]
    )

    def cost_value(self):
        price = self.product.price
        cost = price * self.quantity
        self.cost = cost
        self.save()

    cost = models.DecimalField(
        'Стоимость',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
        )

    class Meta:
        verbose_name = 'Состав заказа'
        verbose_name_plural = 'Состав заказов'

    def __str__(self):
        return self.order.firstname


class Geolocation(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=50,
        unique=True
    )
    longitude = models.CharField('Долгота', max_length=10)
    latitude = models.CharField('Широта', max_length=10)
    last_update = models.DateField(
        'Дата последнего обновления',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Геолокация'
        verbose_name_plural = 'Геолокации'

    def __str__(self):
        return self.address
