# Generated by Django 5.0.8 on 2024-11-12 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0025_alter_professioanlvendorinquiry_preferred_method_of_contact_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professioanlvendorinquiry',
            name='service_skill',
            field=models.CharField(max_length=50),
        ),
    ]
