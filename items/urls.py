from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("buy/<int:item_id>/", views.buy_item, name="buy_item"),
    path("buy/order/<int:order_id>/", views.buy_order, name="buy_order"),
    path("item/<int:item_id>/", views.item_page, name="item_page"),
    path("order/<int:order_id>/", views.order_page, name="order_page"),
]
