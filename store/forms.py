from django import forms

from  .models import Comment, Order


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'body', 'stars', ]


class AddToCartProductForm(forms.Form):
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 31)]
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)

    inplace = forms.BooleanField(required=False, widget=forms.HiddenInput)


# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = Order
#         fields = ['customer', 'status', ]
#         # widgets = {
#         #     'address': forms.Textarea(attrs={'rows': 3}),
#         #     'order_note': forms.Textarea(attrs={
#         #         'rows': 5,
#         #         'placeholder': 'If you have any notes please enter here otherwise leave it empty.',
#         #     }),
#         # }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'province', 'city', 'address', 'postal_code', 'phone_number', 'order_note']
