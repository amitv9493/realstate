# Generated by Django 5.0.8 on 2024-10-19 15:56

import django.db.models.deletion
import realstate_new.task.models.verification_image
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('task', '0080_runnertask_vendor_company_name_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VerificationDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('image', models.ImageField(upload_to=realstate_new.task.models.verification_image.get_upload_to)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
    ]