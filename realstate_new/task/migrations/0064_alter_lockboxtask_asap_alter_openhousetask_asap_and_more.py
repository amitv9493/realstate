# Generated by Django 5.0.8 on 2024-10-09 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0063_lockboxtask_audio_file_openhousetask_audio_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockboxtask',
            name='asap',
            field=models.BooleanField(default=False, verbose_name='As Soon As Possible'),
        ),
        migrations.AlterField(
            model_name='openhousetask',
            name='asap',
            field=models.BooleanField(default=False, verbose_name='As Soon As Possible'),
        ),
        migrations.AlterField(
            model_name='professionalservicetask',
            name='asap',
            field=models.BooleanField(default=False, verbose_name='As Soon As Possible'),
        ),
        migrations.AlterField(
            model_name='runnertask',
            name='asap',
            field=models.BooleanField(default=False, verbose_name='As Soon As Possible'),
        ),
        migrations.AlterField(
            model_name='showingtask',
            name='asap',
            field=models.BooleanField(default=False, verbose_name='As Soon As Possible'),
        ),
        migrations.AlterField(
            model_name='signtask',
            name='asap',
            field=models.BooleanField(default=False, verbose_name='As Soon As Possible'),
        ),
    ]
