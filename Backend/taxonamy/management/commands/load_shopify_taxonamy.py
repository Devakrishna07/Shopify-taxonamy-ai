import urllib.request

from django.core.management.base import BaseCommand

from taxonamy.models import TaxonomyCategory


TAXONOMY_URL = (
    "https://raw.githubusercontent.com/"
    "Shopify/product-taxonomy/main/"
    "dist/en/categories.txt"
)


class Command(BaseCommand):

    help = "Load Shopify Standard Product Taxonomy categories"

    def handle(self, *args, **options):

        self.stdout.write(
            "Downloading Shopify taxonomy..."
        )

        response = urllib.request.urlopen(
            TAXONOMY_URL
        )

        content = response.read().decode(
            "utf-8"
        )

        lines = content.splitlines()

        created = 0
        updated = 0

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            parts = [
                part.strip()
                for part in line.split(">")
            ]

            if not parts:
                continue

            name = parts[-1]

            full_name = " > ".join(
                parts
            )

            level = len(parts) - 1

            shopify_id = (
                full_name.lower()
                .replace(" ", "-")
                .replace("&", "and")
                .replace("/", "-")
            )

            parent_id = None

            if len(parts) > 1:

                parent_full_name = " > ".join(
                    parts[:-1]
                )

                parent_id = (
                    parent_full_name.lower()
                    .replace(" ", "-")
                    .replace("&", "and")
                    .replace("/", "-")
                )

            _, was_created = (
                TaxonomyCategory.objects.update_or_create(
                    shopify_id=shopify_id,
                    defaults={
                        "name": name,
                        "full_name": full_name,
                        "parent_id": parent_id,
                        "level": level,
                        "is_root": level == 0,
                        "is_leaf": True,
                        "is_archived": False,
                    }
                )
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Updated: {updated}"
            )
        )