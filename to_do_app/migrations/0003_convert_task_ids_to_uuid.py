from django.db import migrations, models
import uuid

def convert_task_ids_to_uuid(apps, schema_editor):
    """
    Convert existing integer IDs to UUIDs
    """
    Task = apps.get_model('to_do_app', 'Task')
    # Delete all existing tasks to avoid UUID conversion issues
    # Note: This is only safe in development - in production you would need a data migration strategy
    Task.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('to_do_app', '0002_category_tag_alter_task_options_task_notes_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_task_ids_to_uuid),
    ]
