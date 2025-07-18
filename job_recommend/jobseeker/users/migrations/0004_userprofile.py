# Generated by Django 5.2 on 2025-04-29 11:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_is_active_user_is_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skills', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('experience', models.IntegerField(blank=True, null=True)),
                ('education', models.CharField(blank=True, max_length=255, null=True)),
                ('salary_expectation', models.IntegerField(blank=True, null=True)),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='resume_upload_path')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
