# Generated by Django 3.1.1 on 2024-03-27 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Session',
            new_name='Shift',
        ),
        migrations.RenameField(
            model_name='attendance',
            old_name='session',
            new_name='shift',
        ),
        migrations.RenameField(
            model_name='student',
            old_name='session',
            new_name='shift',
        ),
    ]