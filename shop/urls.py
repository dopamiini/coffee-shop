from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cart/", views.cart, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("dashboard/", views.admin_view, name="dashboard"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    path("orders/", views.orders, name="orders"),
    path("orders/<int:order_id>/", views.view_order, name="view_order"),
    path("profile/", views.user_profile, name="profile"),
    path("register/", views.register, name="register")
]