# Generated by Django 5.0.6 on 2024-06-19 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thecart_auth', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=150, unique=True, verbose_name='username'),
        ),
    ]