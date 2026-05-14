from decimal import Decimal
from typing import Any, Dict, Optional, Tuple

import stripe
from django.conf import settings
from django.core.exceptions import ValidationError


def get_stripe_keys_for_currency(currency: str) -> Tuple[str, str]:
    code = (currency or "usd").lower()
    if code == "eur":
        sk = settings.STRIPE_SECRET_KEY_EUR
        pk = settings.STRIPE_PUBLISHABLE_KEY_EUR
    else:
        sk = settings.STRIPE_SECRET_KEY_USD
        pk = settings.STRIPE_PUBLISHABLE_KEY_USD
    if not sk or not pk:
        raise ValidationError(
            f"Configure STRIPE_SECRET_KEY_{code.upper()} and STRIPE_PUBLISHABLE_KEY_{code.upper()}."
        )
    return sk, pk


def _line_item(
    *,
    name: str,
    description: str,
    unit_amount_cents: int,
    currency: str,
    quantity: int,
    tax_rate_id: Optional[str],
) -> Dict[str, Any]:
    li: Dict[str, Any] = {
        "quantity": quantity,
        "price_data": {
            "currency": currency.lower(),
            "unit_amount": unit_amount_cents,
            "product_data": {
                "name": name,
                "description": (description or "")[:500],
            },
        },
    }
    if tax_rate_id:
        li["tax_rates"] = [tax_rate_id]
    return li


def _checkout_urls(request) -> tuple[str, str]:
    base = (settings.PUBLIC_BASE_URL or "").rstrip("/")
    if not base:
        base = request.build_absolute_uri("/").rstrip("/")
    return f"{base}/?payment=success", f"{base}/?payment=canceled"


def create_checkout_session_for_item(request, item) -> str:
    sk, _ = get_stripe_keys_for_currency(item.currency)
    stripe.api_key = sk
    success_url, cancel_url = _checkout_urls(request)
    cents = int((item.price * Decimal("100")).quantize(Decimal("1")))
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            _line_item(
                name=item.name,
                description=item.description,
                unit_amount_cents=cents,
                currency=item.currency,
                quantity=1,
                tax_rate_id=None,
            )
        ],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.id


def create_checkout_session_for_order(request, order) -> str:
    currency = order.assert_single_currency()
    sk, _ = get_stripe_keys_for_currency(currency)
    stripe.api_key = sk
    success_url, cancel_url = _checkout_urls(request)
    tax_rate_id = order.tax.stripe_tax_rate_id if order.tax_id else None
    line_items = []
    for line in order.lines.select_related("item"):
        cents = int((line.item.price * Decimal("100")).quantize(Decimal("1")))
        line_items.append(
            _line_item(
                name=line.item.name,
                description=line.item.description,
                unit_amount_cents=cents,
                currency=line.item.currency,
                quantity=line.quantity,
                tax_rate_id=tax_rate_id,
            )
        )
    params: Dict[str, Any] = {
        "mode": "payment",
        "line_items": line_items,
        "success_url": success_url,
        "cancel_url": cancel_url,
    }
    if order.discount_id:
        params["discounts"] = [{"coupon": order.discount.stripe_coupon_id}]
    session = stripe.checkout.Session.create(**params)
    return session.id
