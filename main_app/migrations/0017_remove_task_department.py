# Generated by Django 3.1.1 on 2024-04-21 06:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0016_auto_20240421_0727'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='department',
        ),
    ]
