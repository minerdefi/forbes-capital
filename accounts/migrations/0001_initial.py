# Generated by Django 5.1 on 2024-08-31 01:03

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WalletAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cryptocurrency', models.CharField(choices=[('USDT', 'USDT (TRC-20)'), ('BTC', 'BTC'), ('BCH', 'BCH'), ('ETH', 'ETH')], max_length=10, unique=True)),
                ('address', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Deposit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_type', models.CharField(choices=[('USDT', 'USDT (TRC-20)'), ('BTC', 'BTC'), ('BCH', 'BCH'), ('ETH', 'ETH')], default='BTC', max_length=50)),
                ('confirmed', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
