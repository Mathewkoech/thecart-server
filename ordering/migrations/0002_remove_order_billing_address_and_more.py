# Generated by Django 5.0.6 on 2024-07-02 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordering', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
        migrations.RemoveField(
            model_name='order',
            name='total_price',
        ),
        migrations.RemoveField(
            model_name='order',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.AlterField(
            model_name='order',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
