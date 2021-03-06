
"""Cart actions."""
"""Order views."""

# Django
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
# Models
from .models import OrderItem, Order
from products.models import Product

# Local methods
from cart.cart import Cart


# Libraries
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

# Django
from django.conf import settings

# Libraries
from rest_framework.response import Response


class Orders(object):
    # Get cart items and user data
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        user = request.user
        self.user = user
    
    def stock_validate(self):
        # Validate stock of products
        flag = False
        if len(self.cart.items()) > 0:
            for key, value in self.cart.items():
                product = get_object_or_404(Product, id=value['product_id'])
                if product.amount_avaliable < value['quantity']:
                    flag = True
                    return 'This products it´s out of stock: ' + str(value['product_id']), status.HTTP_204_NO_CONTENT, flag
            return 'Products with stock.', status.HTTP_200_OK, flag
        else:
            return 'You don´t have products in your shopping cart.', status.HTTP_204_NO_CONTENT, flag

    def order_create(self):
        # Create order
        if len(self.cart.items()) > 0:
            order = Order.objects.create(
                user = self.user,
                paid = True
            )

            for key, value in self.cart.items():
                product = get_object_or_404(Product, id=value['product_id'])
                product_amount_avaliable = product.amount_avaliable - value['quantity']
                Product.objects.filter(id=value['product_id']).update(amount_avaliable=product_amount_avaliable)
                
                OrderItem.objects.create(
                    order = order,
                    product = product,
                    price = value['price'],
                    quantity = value['quantity']
                )
            return 'Your order has been successfully registered.', status.HTTP_200_OK
        else:
            return 'You don´t have products in your shopping cart.', status.HTTP_204_NO_CONTENT