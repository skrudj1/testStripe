from django.contrib import admin

from .models import Discount, Item, Order, OrderLine, Tax


class OrderLineInline(admin.TabularInline):
    model = OrderLine
    extra = 1


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "currency", "id")
    list_filter = ("currency",)
    search_fields = ("name", "description")


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ("name", "stripe_coupon_id")


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "stripe_tax_rate_id")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "discount", "tax")
    inlines = [OrderLineInline]
