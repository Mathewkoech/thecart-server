# Generated by Django 5.0.6 on 2024-07-03 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordering', '0006_alter_orderitem_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='value',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]