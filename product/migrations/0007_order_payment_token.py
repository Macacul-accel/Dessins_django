# Generated by Django 5.1.4 on 2025-01-26 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_alter_order_options_order_shipping_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_token',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
    ]
