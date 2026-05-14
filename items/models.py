from django.db import models
from django.core.exceptions import ValidationError


class Currency(models.TextChoices):
    USD = "usd", "USD"
    EUR = "eur", "EUR"


class Discount(models.Model):
    """Stripe Coupon id (created in Stripe Dashboard or API), e.g. j25BpKn4."""

    name = models.CharField(max_length=255)
    stripe_coupon_id = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Tax(models.Model):
    """Stripe Tax Rate id, e.g. txr_1H..."""

    name = models.CharField(max_length=255)
    stripe_tax_rate_id = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Taxes"

    def __str__(self) -> str:
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        default=Currency.USD,
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.currency.upper()})"


class Order(models.Model):
    """Cart: several items (with quantities), optional discount & tax for Checkout."""

    created_at = models.DateTimeField(auto_now_add=True)
    discount = models.ForeignKey(
        Discount,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    tax = models.ForeignKey(
        Tax,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="orders",
    )
    items = models.ManyToManyField(Item, through="OrderLine", related_name="orders")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk}" if self.pk else "Order (unsaved)"

    def assert_single_currency(self) -> str:
        """Return currency code; raise ValidationError if lines mix currencies."""
        codes = list(self.lines.values_list("item__currency", flat=True))
        if not codes:
            raise ValidationError("Order has no line items.")
        unique = set(codes)
        if len(unique) != 1:
            raise ValidationError("All items in an order must use the same currency.")
        return codes[0]


class OrderLine(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="lines")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="order_lines")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [("order", "item")]

    def __str__(self) -> str:
        return f"{self.quantity}× {self.item}"
