import datetime
from django.core.management.base import BaseCommand
from middlewares.models import RequestDataLog  

class Command(BaseCommand):
    help = 'Deletes records older than 15 days'

    def handle(self, *args, **kwargs):
        # Get the date 15 days ago
        threshold_date = datetime.datetime.now() - datetime.timedelta(days=15)

        # Query to delete records older than 15 days
        old_records = RequestDataLog.objects.filter(timestamp__lt=threshold_date)
        deleted_count, _ = old_records.delete()

        # Output result in the PythonAnywhere logs (Optional)
        self.stdout.write(f"Deleted {deleted_count} records older than 15 days.")
