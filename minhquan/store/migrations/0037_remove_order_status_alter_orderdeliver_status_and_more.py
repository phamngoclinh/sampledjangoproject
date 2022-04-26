# Generated by Django 4.0.3 on 2022-04-19 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0036_rename_status_orderstatus_name_remove_order_status1_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.AlterField(
            model_name='orderdeliver',
            name='status',
            field=models.CharField(choices=[('draft', 'Đang tiếp nhận'), ('processing', 'Đang xử lý'), ('shipping', 'Đang giao hàng'), ('done', 'Hoàn thành'), ('canceled', 'Đã hủy')], default='draft', max_length=100),
        ),
        migrations.DeleteModel(
            name='OrderStatus',
        ),
    ]