import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "If BOOTSTRAP_ADMIN_USER and BOOTSTRAP_ADMIN_PASSWORD are set, "
        "creates that superuser when missing (handy on Render without Shell)."
    )

    def handle(self, *args, **options):
        username = os.environ.get("BOOTSTRAP_ADMIN_USER", "").strip()
        password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD", "").strip()
        if not username or not password:
            return
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return
        email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL", "admin@example.com").strip() or "admin@example.com"
        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS("Created superuser: %s" % username))
