# Generated by Django 4.0.3 on 2022-04-19 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0042_rename_deliver_order_orderdeliver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdeliver',
            name='status',
            field=models.CharField(choices=[('draft', 'Chưa thanh toán'), ('confirmed', 'Đã tiếp nhận'), ('processing', 'Đang xử lý'), ('shipping', 'Đang giao hàng'), ('done', 'Hoàn thành'), ('canceled', 'Đã hủy')], default='draft', max_length=100),
        ),
    ]