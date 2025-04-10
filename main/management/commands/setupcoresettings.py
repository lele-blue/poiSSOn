from django.core.management.base import BaseCommand

from main.core_settings import CORE_SETTINGS
from main.models import CoreSetting

class Command(BaseCommand):
    help = "populates the core settings table with defaults. must be run before first run and after updates"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        for key, setting in CORE_SETTINGS.items():
            if not CoreSetting.objects.filter(key=key).exists():
                CoreSetting(key=key, value=setting["default"]).save()

        self.stdout.write(
            self.style.SUCCESS('Successfully setup the core settings.')
        )
