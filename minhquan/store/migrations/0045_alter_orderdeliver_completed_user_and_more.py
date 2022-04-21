# Generated by Django 4.0.3 on 2022-04-22 00:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0044_order_created_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdeliver',
            name='completed_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='completed_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='orderdeliver',
            name='created_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
