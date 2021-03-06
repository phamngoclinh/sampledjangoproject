# Generated by Django 3.2.12 on 2022-04-16 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0025_auto_20220416_1726'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pos',
            old_name='total',
            new_name='amount_discount',
        ),
        migrations.RenameField(
            model_name='posdetail',
            old_name='discount',
            new_name='price_discount',
        ),
        migrations.RenameField(
            model_name='posdetail',
            old_name='price',
            new_name='price_unit',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='cost',
            new_name='sub_price',
        ),
        migrations.AddField(
            model_name='pos',
            name='amount_sub_total',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='pos',
            name='amount_total',
            field=models.FloatField(default=0),
        ),
    ]
