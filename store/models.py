from django.db.models import Avg, Sum
from django.db import models
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from uuid import uuid4
from django.db.models.signals import post_save
from django.dispatch import receiver

class Category(models.Model):
    title = models.CharField(_("Title"), max_length=255)
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True)
    description = models.CharField(_("Description"), max_length=500, blank=True)
    top_product = models.ForeignKey('Product', verbose_name=_("Top Product"), on_delete=models.SET_NULL, null=True, related_name='+', blank=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Category")
    

class Discount(models.Model):
    title = models.CharField(_("Title"), max_length=255, null=True)
    discount = models.FloatField(_("Discount"))
    description = models.CharField(_("Description"), max_length=255)

    def __str__(self):
        return f'{self.discount}% | {self.description}'
    
    class Meta:
        verbose_name = _("Discount")
        verbose_name_plural = _("Discount")


class Product(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    category = models.ForeignKey(Category, verbose_name=_("Category"), on_delete=models.PROTECT, related_name='products')
    slug = models.SlugField(_("Slug"))
    description = models.TextField(_("Description"))
    price = models.DecimalField(_("Price"), decimal_places=0, max_digits=10, default=0)
    inventory = models.PositiveIntegerField(_("Inventory"), default=0)
    active= models.BooleanField(_("Active"), default=True)
    datetime_created = models.DateTimeField(_("Date time Created"), auto_now_add=True)
    datetime_modified = models.DateTimeField(_("Date time modified"), auto_now=True)
    discount = models.ManyToManyField(Discount, verbose_name=_("Discount"), blank=True, related_name='products')
    main_image = models.ForeignKey('ProductImage', on_delete=models.SET_NULL, related_name='main_image', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.main_image and self.images.exists():
            self.main_image = self.images.first()
        super().save(*args, **kwargs)

    @property
    def total_sales(self):
        return self.order_items.aggregate(total_sales=Sum('quantity'))['total_sales'] or 0

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse("product_detail", args=[self.pk])
    
    def average_rating(self):
        ave_rate = self.comments.aggregate(Avg('stars'))['stars__avg'] or 0
        return [i for i in range(int(ave_rate))]
    
    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Product")


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', blank=True, )
    image = models.ImageField(_("Product image"), upload_to='product/product_cover/')

    def __str__(self):
        return f"Image of {self.product.name}"

    
class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    phone_number = models.CharField(_("Phone Number"), max_length=15)
    birth_date = models.DateField(_("Birth Date"),null=True, blank=True)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'

    class Meta:
        permissions = [
            ('send_private_email', 'Can send private email to user by the button'),
        ]
        verbose_name = _("Customer")
        verbose_name_plural = _("Customer")


class Address(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, primary_key=True)
    province = models.CharField(_("Province"), max_length=255)
    city = models.CharField(_("City"), max_length=255)
    street = models.CharField(_("Street"), max_length=255)

    class Meta:
        verbose_name = _("Address")
        verbose_name_plural = _("Address")


class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('Customer'))
    is_paid = models.BooleanField(_('Is Paid?'), default=False)

    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    phone_number = models.CharField(_('Phone Number'), max_length=15, default='-')
    address = models.CharField(_('Address'), max_length=700)

    city = models.CharField(_('City'), max_length=100, default='-')  
    province = models.CharField(_('Province'), max_length=100, default='-')  
    postal_code = models.CharField(_('Postal Code'), max_length=20, default='-')

    order_note = models.CharField(_('Order Notes'), max_length=700, blank=True)

    datetime_created = models.DateTimeField(_('Created Date'), auto_now_add=True)
    datetime_modified = models.DateTimeField(_('Modified Date'), auto_now=True)

    tracking_code = models.CharField(_('Tracking Code'), max_length=9, unique=True, blank=True, null=True)


    def __str__(self):
        return f'Order {self.id}'
    

    def get_total_price(self):
        return sum(item.quantity * item.price for item in self.items.all())
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Order")


@receiver(post_save, sender=Order)
def generate_tracking_code(sender, instance, created, **kwargs):

    if created and not instance.tracking_code:
        tracking_code = str(uuid4())[:9]
        instance.tracking_code = tracking_code
        instance.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=_("Order"), on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(_("Quantity"), default=1)
    price = models.PositiveIntegerField(_("Price"))

    @property
    def total_price(self):
        if self.quantity is not None and self.price is not None:
            return self.quantity * self.price
        return 0

    def __str__(self):
        return f'OrderItem {self.id}: {self.product} X {self.quantity} (price: {self.price})'
    
    class Meta:
        unique_together = [['order', 'product']]
        verbose_name = _("OrderItem")
        verbose_name_plural = _("OrderItem")


class Comment(models.Model):
    PRODUCT_STARS = [
        ('1', _('Very Bad')),
        ('2', _('Bad')),
        ('3', _('Normal')),
        ('4', _('Good')),
        ('5', _('Perfect')),
    ]
    COMMENT_STATUS_WAITING = 'w'
    COMMENT_STATUS_APPROVED = 'a'
    COMMENT_STATUS_NOT_APPROVED = 'na'
    COMMENT_STATUS = [
        (COMMENT_STATUS_WAITING, 'Waiting'),
        (COMMENT_STATUS_APPROVED, 'Approved'),
        (COMMENT_STATUS_NOT_APPROVED, 'Not Approved'),
    ]
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(_("Name"), max_length=255)
    body = models.TextField(_("Comment text"))
    stars = models.CharField(max_length=10, choices=PRODUCT_STARS, verbose_name=_('Your score?'), default='3')
    datetime_created = models.DateTimeField(_("Date time Created"), auto_now_add=True)
    status = models.CharField(_("Status"), max_length=2, choices=COMMENT_STATUS, default=COMMENT_STATUS_WAITING)

    def stars_as_integer(self):
        return [i for i in range(int(self.stars))]
    
    def get_absolute_url(self):
        return reverse("product_detail", args={self.product.id})
    
    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comment")
    

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(_("Created at:"), auto_now_add=True)

    class Meta:
        verbose_name = _("Cart")
        verbose_name_plural = _("Cart")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_("Cart"), on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveSmallIntegerField(_("Quantity"))

    class Meta:
        unique_together = [['cart', 'product']]
        verbose_name = _("CartItem")
        verbose_name_plural = _("CartItem")


class Blog(models.Model):
    title =models.CharField(_("Title"), max_length=255)
    post = models.TextField(_("Post text"))
    author = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    datetime_created = models.DateTimeField(_("Date time Created"), auto_now_add=True)
    datetime_modified = models.DateTimeField(_("Date time modified"), auto_now=True)
    image = models.ImageField(_("Post image"), upload_to='blog/post_cover/', blank=True, )
    status = models.CharField(_("Status"), max_length=10, choices=[('draft', 'Draft'), ('published', 'Published')], default='draft')

    def __str__(self):
        return f'{self.author}: {self.title}'
    
    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blog")


class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist', verbose_name=_("User"))
    products = models.ManyToManyField(Product, related_name='wishlists', verbose_name=_("Products"))

    def __str__(self):
        return f"Wishlist of {self.user.username}"

    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlists")

