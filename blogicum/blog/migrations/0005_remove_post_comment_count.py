# Generated by Django 3.2.16 on 2024-06-06 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_post_comment_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='comment_count',
        ),
    ]
