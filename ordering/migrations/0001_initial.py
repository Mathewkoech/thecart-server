# Generated by Django 5.0.6 on 2024-06-18 20:32

import common.utils
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
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
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('delivered_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rider', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_order', to=settings.AUTH_USER_MODEL)),
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
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='ordering.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.product')),
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
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='modified_%(class)s', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_shipping', to='ordering.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_shipping', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'shipping',
            },
        ),
        migrations.AddField(
            model_name='order',
            name='shipping',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_shipping', to='ordering.shipping'),
        ),
    ]
