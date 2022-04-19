# Generated by Django 4.0.3 on 2022-04-18 16:34

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0034_rename_pos_order_rename_posdetail_orderdetail_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('updated_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('active', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('processing', 'Processing'), ('shipping', 'Shipping'), ('done', 'Done')], default='draft', max_length=100)),
                ('started_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('completed_date', models.DateTimeField(blank=True, default=None, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='order',
            name='status1',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.orderstatus'),
        ),
    ]
