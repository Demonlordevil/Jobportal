# Generated by Django 5.2 on 2025-05-22 06:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_jobapplication_status_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobapplication',
            name='resume_link',
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='resume_file',
            field=models.FileField(blank=True, null=True, upload_to='resume_upload_path'),
        ),
    ]
