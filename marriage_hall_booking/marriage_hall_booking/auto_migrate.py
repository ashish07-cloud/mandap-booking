import os
import time
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "marriage_hall_booking.settings")
django.setup()

max_retries = 5

for attempt in range(max_retries):
    try:
        print("⚙️ Running makemigrations...")
        call_command("makemigrations", interactive=False, verbosity=2)

        print("📦 Running migrate...")
        call_command("migrate", interactive=False, verbosity=2)

        print("✅ Migration succeeded.")
        break
    except Exception as e:
        print(f"❌ Attempt {attempt + 1} failed with error:\n{e}")
        time.sleep(5)
else:
    print("❌ All migration attempts failed.")
