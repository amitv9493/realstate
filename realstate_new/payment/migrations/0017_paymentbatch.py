# Generated by Django 5.0.8 on 2024-10-09 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0016_remove_paypalpayementhistory_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentBatch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('batch_id', models.CharField(max_length=50)),
                ('payment_processing', models.ManyToManyField(to='payment.paypalpayementhistory')),
            ],
        ),
    ]