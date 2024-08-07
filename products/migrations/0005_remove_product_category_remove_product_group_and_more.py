# Generated by Django 5.0.6 on 2024-06-28 17:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_remove_category_slug_remove_group_slug_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.RemoveField(
            model_name='product',
            name='group',
        ),
        migrations.RemoveField(
            model_name='product',
            name='subgroup',
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.category'),
        ),
        migrations.AddField(
            model_name='product',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.group'),
        ),
        migrations.AddField(
            model_name='product',
            name='subgroup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.subgroup'),
        ),
    ]
