# Generated by Django 5.0.8 on 2024-10-26 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('master', '0023_professioanlvendorinquiry'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professioanlvendorinquiry',
            name='additional_notes',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='professioanlvendorinquiry',
            name='mile_radius_preference',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Area Covered'),
        ),
        migrations.AlterField(
            model_name='professioanlvendorinquiry',
            name='preferred_name',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
    ]
