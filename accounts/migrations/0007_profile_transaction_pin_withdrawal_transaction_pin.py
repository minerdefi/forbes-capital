# Generated by Django 5.1 on 2024-08-31 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_walletaddress'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='transaction_pin',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='withdrawal',
            name='transaction_pin',
            field=models.CharField(default=0, max_length=6),
            preserve_default=False,
        ),
    ]
