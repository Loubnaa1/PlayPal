# Generated by Django 5.0.4 on 2024-05-13 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_like'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='like',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='like',
            name='post',
        ),
        migrations.RemoveField(
            model_name='like',
            name='user',
        ),
    ]
