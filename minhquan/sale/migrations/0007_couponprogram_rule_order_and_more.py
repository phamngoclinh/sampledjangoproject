# Generated by Django 4.0.3 on 2022-04-29 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0006_alter_couponprogram_rule_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponprogram',
            name='rule_order',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='couponprogram',
            name='rule_customer',
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name='couponprogram',
            name='rule_product',
            field=models.JSONField(null=True),
        ),
    ]
