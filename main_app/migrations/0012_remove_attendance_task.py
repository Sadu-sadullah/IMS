# Generated by Django 3.1.1 on 2024-04-21 03:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0011_remove_task_assigned_interns'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attendance',
            name='task',
        ),
    ]
