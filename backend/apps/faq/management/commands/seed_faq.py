# apps/faq/management/commands/seed_faq.py
from django.core.management.base import BaseCommand
from apps.faq.models import FAQCategory, FAQItem, FINTECH_FAQ


class Command(BaseCommand):
    help = "Seed the database with built-in fintech FAQ data"

    def handle(self, *args, **options):
        created_count = 0
        for entry in FINTECH_FAQ:
            category, _ = FAQCategory.objects.get_or_create(name=entry["category"])
            _, created = FAQItem.objects.get_or_create(
                question=entry["question"],
                defaults={
                    "category": category,
                    "answer": entry["answer"],
                    "keywords": entry["keywords"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {created_count} new FAQ items created "
                f"({len(FINTECH_FAQ) - created_count} already existed)."
            )
        )
