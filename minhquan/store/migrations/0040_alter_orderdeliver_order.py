# Generated by Django 4.0.3 on 2022-04-19 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0039_rename_status_order_deliver'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdeliver',
            name='order',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='order', to='store.order'),
        ),
    ]
