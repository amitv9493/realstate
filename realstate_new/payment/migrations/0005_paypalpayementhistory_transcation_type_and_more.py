# Generated by Django 5.0.7 on 2024-08-04 05:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0004_alter_wallet_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='paypalpayementhistory',
            name='transcation_type',
            field=models.CharField(choices=[('WITHDRAW', 'WITHDRAW'), ('DIPOSIT', 'DIPOSIT')], default='WITHDRAW', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='paypalpayementhistory',
            name='wallet',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='payment.wallet'),
            preserve_default=False,
        ),
    ]
