# Generated manually for initial schema

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Discount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("stripe_coupon_id", models.CharField(max_length=255, unique=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Tax",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("stripe_tax_rate_id", models.CharField(max_length=255, unique=True)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "Taxes"},
        ),
        migrations.CreateModel(
            name="Item",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("price", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(choices=[("usd", "USD"), ("eur", "EUR")], default="usd", max_length=3)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "discount",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="items.discount",
                    ),
                ),
                (
                    "tax",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="items.tax",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderLine",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("quantity", models.PositiveIntegerField(default=1)),
                (
                    "item",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="order_lines", to="items.item"),
                ),
                (
                    "order",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lines", to="items.order"),
                ),
            ],
        ),
        migrations.AddField(
            model_name="order",
            name="items",
            field=models.ManyToManyField(related_name="orders", through="items.OrderLine", to="items.item"),
        ),
        migrations.AlterUniqueTogether(
            name="orderline",
            unique_together={("order", "item")},
        ),
    ]
