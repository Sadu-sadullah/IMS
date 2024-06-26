# Generated by Django 3.1.1 on 2024-03-27 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_auto_20240327_1314'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedbackIntern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback', models.TextField()),
                ('reply', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveReportIntern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=60)),
                ('message', models.TextField()),
                ('status', models.SmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationIntern',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='StudentResult',
            new_name='InternResult',
        ),
        migrations.RemoveField(
            model_name='leavereportstudent',
            name='student',
        ),
        migrations.RemoveField(
            model_name='notificationstudent',
            name='student',
        ),
        migrations.RenameField(
            model_name='attendancereport',
            old_name='student',
            new_name='intern',
        ),
        migrations.RenameField(
            model_name='internresult',
            old_name='student',
            new_name='intern',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[(1, 'HOD'), (2, 'Staff'), (3, 'Intern')], default=1, max_length=1),
        ),
        migrations.RenameModel(
            old_name='Student',
            new_name='Intern',
        ),
        migrations.DeleteModel(
            name='FeedbackStudent',
        ),
        migrations.DeleteModel(
            name='LeaveReportStudent',
        ),
        migrations.DeleteModel(
            name='NotificationStudent',
        ),
        migrations.AddField(
            model_name='notificationintern',
            name='intern',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.intern'),
        ),
        migrations.AddField(
            model_name='leavereportintern',
            name='intern',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.intern'),
        ),
        migrations.AddField(
            model_name='feedbackintern',
            name='intern',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.intern'),
        ),
    ]
