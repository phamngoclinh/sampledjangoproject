# Generated by Django 3.2.12 on 2022-04-16 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_product_coupon_programs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='coupon_programs',
        ),
    ]
