# Generated by Django 3.2.16 on 2024-06-06 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_auto_20240606_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comment_count',
            field=models.IntegerField(default=0, verbose_name='Комментарии'),
        ),
    ]
