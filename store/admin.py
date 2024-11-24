from django.contrib import admin, messages
from django.db.models import Count, Sum, F
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from jalali_date.admin import ModelAdminJalaliMixin
from django.utils.http import urlencode 

from . import models


@admin.register(models.Customer)
class CustomerAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', ]
    list_per_page = 10
    ordering = ['user__last_name', 'user__first_name', ]
    search_fields = ['user__first_name__istartswith', 'user__last_name__istartswith', ]

    def first_name(self, customer):
        return customer.user.first_name

    def last_name(self, customer):
        return customer.user.last_name

    def email(self, customer):
        return customer.user.email


class CommentInline(admin.TabularInline):
    model = models.Comment
    fields = ['name', 'body', 'stars', 'status', ]
    extra = 0
    

class ProductImageInline(admin.TabularInline): # یا StackedInline
    model = models.ProductImage
    extra = 5  # تعداد فیلدهای خالی برای آپلود تصاویر اضافی


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'inventory', 'price', 'category', 'num_of_comments', 'inventory_status', 'active', 'main_image', 'total_sales', 'total', ]
    list_per_page = 10
    search_fields = ['name', ]
    list_editable = ['price', ]
    list_filter = ['datetime_created', 'category', ]
    actions = ['clear_inventory', ]
    search_fields = ['name', ]
    prepopulated_fields = {'slug': ('name', )}

    inlines = [
        ProductImageInline,
        CommentInline,
    ]

    def total_sales(self, obj):
        return obj.total_sales
    
    def total(self, obj):
        return obj.total_sales * obj.price
    
    total_sales.short_description = _('Total Sales')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('comments').annotate(comments_count=Count('comments'))

    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    # inventory_status.boolean = True
    inventory_status.short_description = _('Low stock')

    @admin.display(ordering='comments_count', description=_('# comments'))
    def num_of_comments(self, product):
        url = reverse('admin:store_comment_changelist') + '?' + urlencode({'product__id': product.id, })
        return format_html('<a href="{}">{}</a>', url, product.comments_count)

    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        update_count = queryset.update(inventory=0)
        self.message_user(request, f'{update_count} products inventories were updated.', messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        if not obj.main_image:
            first_image = obj.images.first()
            if first_image:
                obj.main_image = first_image
        super().save_model(request, obj, form, change)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'top_product', ]


class OrderItemInline(admin.TabularInline):
    model = models.OrderItem
    fields = ['product', 'quantity', 'price', 'total_price']
    readonly_fields = ['total_price']
    extra = 0


@admin.register(models.Order)
class OrderAdmin(ModelAdminJalaliMixin, admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'datetime_created', 'is_paid', 'tracking_code', ]

    inlines = [
        OrderItemInline,
    ]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            total_quantity=Sum('items__quantity'),
            total_revenue=Sum(F('items__quantity') * F('items__price'))
        )
        return queryset


@admin.register(models.OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price' ]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'body', 'stars', 'status', ]
    list_editable = ['status', ]
    list_per_page = 10
    ordering = ['-datetime_created', ]
    list_display_links = ['id', 'product', ]
    autocomplete_fields = ['product', ]


@admin.register(models.Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'discount', 'description', ]
    list_editable = ['description', ]
    list_per_page = 10


class CartItemInline(admin.TabularInline):
    model = models.CartItem
    fields = ['id', 'product', 'quantity', ]
    extra = 0
    min_num = 1


@admin.register(models.Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', ]
    inlines = [CartItemInline, ]


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'status', ]


@admin.register(models.Wishlist)
class Wishlist(admin.ModelAdmin):
    list_display = ['id', 'user', ]
