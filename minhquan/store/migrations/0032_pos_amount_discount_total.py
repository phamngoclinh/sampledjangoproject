# Generated by Django 3.2.12 on 2022-04-17 01:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0031_posdetail_sub_price_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='pos',
            name='amount_discount_total',
            field=models.FloatField(default=0),
        ),
    ]