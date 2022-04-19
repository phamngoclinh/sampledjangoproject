# Generated by Django 4.0.3 on 2022-04-18 17:12

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0035_orderstatus_order_status1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderstatus',
            old_name='status',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='order',
            name='status1',
        ),
        migrations.RemoveField(
            model_name='orderstatus',
            name='completed_date',
        ),
        migrations.RemoveField(
            model_name='orderstatus',
            name='started_date',
        ),
        migrations.CreateModel(
            name='OrderDeliver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('updated_date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('active', models.BooleanField(default=True)),
                ('completed', models.BooleanField(default=False)),
                ('started_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('completed_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('completed_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='completed_user', to=settings.AUTH_USER_MODEL)),
                ('created_user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_user', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='store.order')),
                ('status', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='store.orderstatus')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
