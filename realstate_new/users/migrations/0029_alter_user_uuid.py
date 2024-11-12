# Generated by Django 5.0.8 on 2024-11-03 08:05

import uuid
from django.db import migrations, models


def generate_uuids(apps, schema_editor):
    User = apps.get_model("users", "User")
    for user in User.objects.all():
        user.uuid = uuid.uuid4()
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0028_alter_user_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4),
        ),
        migrations.RunPython(generate_uuids),
    ]