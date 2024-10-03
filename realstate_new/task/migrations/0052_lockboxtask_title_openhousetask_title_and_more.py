# Generated by Django 5.0.8 on 2024-10-03 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0051_alter_lockboxtask_instructions'),
    ]

    operations = [
        migrations.AddField(
            model_name='lockboxtask',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='openhousetask',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='professionalservicetask',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='runnertask',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='showingtask',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AddField(
            model_name='signtask',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
    ]
