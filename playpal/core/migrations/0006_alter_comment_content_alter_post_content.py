# Generated by Django 5.0.4 on 2024-05-13 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_comment_content_alter_post_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=models.CharField(max_length=250),
        ),
        migrations.AlterField(
            model_name='post',
            name='content',
            field=models.TextField(max_length=400),
        ),
    ]