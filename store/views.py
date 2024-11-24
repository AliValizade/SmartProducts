import uuid
from django.db.models import Avg, Count
from django.db.models.query import QuerySet
from django.shortcuts import reverse, get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.views.generic import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext as _

from .models import *
from .forms import CommentForm, AddToCartProductForm, OrderForm
from cart.cart import Cart

class HomePageView(TemplateView):
    queryset = Product.objects.select_related('category').prefetch_related('comments')
    template_name = 'home.html'
    context_object_name = 'products'

    def get_new_products(self):
        return self.queryset.order_by('-datetime_created')[:3]

    def get_popular_products(self):
        return self.queryset.annotate(average_stars=Avg('comments__stars')).order_by('-average_stars')[:3]
    
    def get_best_selling_products(self):
        return self.queryset.annotate(sales_count=Count('cart_items')).order_by('-sales_count')[:3]

    # تابع جدید برای گرفتن 3 پست آخر از مدل بلاگ
    def get_latest_posts(self):
        return Blog.objects.order_by('-datetime_created')[:3]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_posts'] = self.get_latest_posts()
        return context
    

class AboutUsView(TemplateView):
    template_name = 'store/aboutus.html'


class ProductListView(ListView):
    # model = Product
    queryset = Product.objects.select_related('category').prefetch_related('comments')
    template_name = 'store/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(average_stars=Avg('comments__stars'))
        return queryset
    

class WomenProductListView(ListView):
    # model = Product
    queryset = Product.objects.select_related('category').filter(active=True)
    template_name = 'store/women_shop.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(category__title='زنانه')


class MenProductListView(ListView):
    # model = Product
    queryset = Product.objects.select_related('category').filter(active=True)
    template_name = 'store/men_shop.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(category__title='مردانه')


class NewProductsListView(ListView):
    queryset = Product.objects.select_related('category').filter(active=True).order_by('-datetime_created')[:4]  # نمایش ۱۰ محصول جدید
    template_name = 'store/new_products.html'
    context_object_name = 'new_products'


def popular_products(request):
    popular_products = Product.objects.select_related('category').prefetch_related('comments').annotate(avg_rating=Avg('comments__stars')).order_by('-avg_rating')[:6]
    return render(request, 'store/popular_product.html', {'popular_products': popular_products})


class BestSellProductsView(TemplateView):
    template_name = 'store/best_sell_product.html'

    def get_best_sell_products(self):
        return Product.objects.select_related('category').filter(active=True).annotate(sales_count=Count('cart_items')).order_by('-sales_count')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['best_sell_products'] = self.get_best_sell_products()
        return context
    

class GalleryListView(ListView):
    # model = Product
    queryset = Product.objects.filter(active=True)
    template_name = 'store/men_shop.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(category__title='مردانه')
    

class ProductDetailView(DetailView):
    queryset = Product.objects.select_related('category').prefetch_related('comments').all()
    template_name = 'store/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['add_to_cart_form'] = AddToCartProductForm()
        return context


class CommentCreateView(CreateView):
    model = Comment
    form_class = CommentForm
 
    # def get_success_url(self):
    #     return reverse('product_detail')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author = self.request.user

        product_id = int(self.kwargs['product_id'])
        product = get_object_or_404(Product, id=product_id)
        obj.product = product

        messages.success(self.request, _('Comment successfully created.'))

        return super().form_valid(form)


class MyAccountView(TemplateView):
    template_name = 'store/my_account.html'


class PaymentView(TemplateView):
    template_name = 'store/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.request.session.get('order_id')

        try:
            order = Order.objects.get(id=order_id)
            context['tracking_code'] = order.tracking_code
        except Order.DoesNotExist:
            context['tracking_code'] = None

        return context


def posts_list_view(request):
    posts = Blog.objects.filter(status='published')
    context = {
        'posts_list': posts,
    }
    return render(request, 'store/blog.html', context)


@login_required
def order_checkout(request):
    order_form = OrderForm()
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, _('Your cart is Empty! Please add some products.'))
        return redirect('product_list')

    if request.method == 'POST':
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order_obj = order_form.save(commit=False)
            order_obj.customer = request.user
            order_obj.save()

            for item in cart:
                product = item['product_obj']
                OrderItem.objects.create(
                    order=order_obj,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price,
                )

            cart.clear()

            request.user.first_name = order_obj.first_name
            request.user.last_name = order_obj.last_name
            request.user.save()

            messages.success(request, _('Your order has successfully placed.'))

            request.session['order_id'] = order_obj.id
            return redirect('payment_process')

    return render(request, 'store/checkout.html', context={
        'form': order_form,
    })


class WishlistView(TemplateView):
    template_name = 'store/wishlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user
        wishlist = Wishlist.objects.get(user=current_user)
        context['wishlist'] = wishlist.products.all()
        return context


def add_to_wishlist(request, product_id):
    if not request.user.is_authenticated:
        return redirect('account_login')

    product = get_object_or_404(Product, id=product_id)

    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if product not in wishlist.products.all():
        wishlist.products.add(product)

    return redirect('wishlist')
