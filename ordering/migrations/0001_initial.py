# Generated by Django 5.0.6 on 2024-06-20 07:37

import common.utils
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('order_number', models.CharField(default=common.utils.generate_random_number, max_length=30, unique=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Shipped', 'Shipped')], default='Pending', max_length=20)),
                ('order_status', models.CharField(choices=[('confirmed', 'confirmed'), ('not_confirmed', 'not_confirmed')], default='not_confirmed', max_length=20, null=True)),
                ('total', models.DecimalField(decimal_places=4, max_digits=14, null=True)),
                ('discount', models.DecimalField(decimal_places=4, max_digits=14, null=True)),
                ('total_after_discount', models.DecimalField(decimal_places=4, max_digits=14, null=True)),
                ('items', models.PositiveIntegerField(default=1)),
                ('first_name', models.CharField(blank=True, max_length=250)),
                ('last_name', models.CharField(blank=True, max_length=250)),
                ('email', models.CharField(blank=True, max_length=250)),
                ('phone', models.CharField(blank=True, max_length=250)),
                ('address', models.CharField(blank=True, max_length=250)),
            ],
            options={
                'db_table': 'order',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=14, null=True)),
                ('price', models.DecimalField(decimal_places=4, default=0, editable=False, max_digits=14)),
                ('value', models.DecimalField(decimal_places=4, default=0, editable=False, max_digits=14)),
            ],
            options={
                'verbose_name_plural': 'Order Items',
                'db_table': 'order_item',
            },
        ),
        migrations.CreateModel(
            name='Shipping',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(null=True)),
                ('postal_code', models.CharField(blank=True, max_length=250)),
                ('address', models.CharField(blank=True, max_length=250)),
                ('town', models.CharField(blank=True, max_length=250)),
                ('default', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'shipping',
            },
        ),
    ]
