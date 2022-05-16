# Generated by Django 4.0.4 on 2022-05-13 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sale', '0008_alter_couponprogram_rule_customer_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='sale.partner'),
        ),
        migrations.AddField(
            model_name='couponprogram',
            name='discount_apply_on_type',
            field=models.CharField(choices=[('order', 'Order'), ('cheapest_product', 'Cheapest product'), ('specific_product', 'Specific product')], default='order', max_length=50),
        ),
        migrations.AddField(
            model_name='couponprogram',
            name='discount_max_amount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='couponprogram',
            name='free_product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='free_product_couponprograms', to='sale.product'),
        ),
        migrations.AddField(
            model_name='couponprogram',
            name='free_product_total',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='couponprogram',
            name='reward_type',
            field=models.CharField(choices=[('discount', 'Discount'), ('free_product', 'Free product')], default='discount', max_length=50),
        ),
        migrations.AlterField(
            model_name='couponprogram',
            name='discount',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='couponprogram',
            name='products',
            field=models.ManyToManyField(blank=True, null=True, related_name='couponprograms', to='sale.product'),
        ),
    ]