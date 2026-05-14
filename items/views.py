import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET

from .models import Item, Order
from .stripe_utils import (
    create_checkout_session_for_item,
    create_checkout_session_for_order,
    get_stripe_keys_for_currency,
)


@require_GET
def buy_item(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)
    try:
        session_id = create_checkout_session_for_item(request, item)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"session_id": session_id})


@require_GET
def buy_order(request, order_id: int):
    order = get_object_or_404(Order.objects.prefetch_related("lines__item"), pk=order_id)
    try:
        session_id = create_checkout_session_for_order(request, order)
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    return JsonResponse({"session_id": session_id})


@require_GET
def item_page(request, item_id: int):
    item = get_object_or_404(Item, pk=item_id)
    try:
        _, publishable = get_stripe_keys_for_currency(item.currency)
    except Exception as exc:
        return HttpResponse(f"Stripe keys not configured: {exc}", status=500)
    ctx = {
        "item": item,
        "stripe_publishable_key": publishable,
        "buy_url": f"/buy/{item.id}/",
    }
    return render(request, "items/checkout_item.html", ctx)


@require_GET
def order_page(request, order_id: int):
    order = get_object_or_404(
        Order.objects.select_related("discount", "tax").prefetch_related("lines__item"),
        pk=order_id,
    )
    try:
        currency = order.assert_single_currency()
        _, publishable = get_stripe_keys_for_currency(currency)
    except Exception as exc:
        return HttpResponse(str(exc), status=400)
    lines = list(order.lines.select_related("item"))
    ctx = {
        "order": order,
        "lines": lines,
        "stripe_publishable_key": publishable,
        "buy_url": f"/buy/order/{order.id}/",
    }
    return render(request, "items/checkout_order.html", ctx)


@require_GET
def index(request):
    items = Item.objects.all()
    orders = Order.objects.prefetch_related("lines__item").all()[:50]
    payload = {
        "items": [{"id": i.id, "name": i.name, "url": f"/item/{i.id}/"} for i in items],
        "orders": [{"id": o.id, "url": f"/order/{o.id}/"} for o in orders],
    }
    return HttpResponse(
        "<pre>" + json.dumps(payload, indent=2) + "</pre>",
        content_type="text/html; charset=utf-8",
    )
