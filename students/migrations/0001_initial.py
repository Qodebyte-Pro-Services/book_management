# Generated by Django 5.1.8 on 2025-04-25 11:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schools', '0002_alter_school_school_type'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='schools.school')),
            ],
            options={
                'verbose_name_plural': 'Classes',
                'unique_together': {('school', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_number', models.CharField(max_length=50, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=10)),
                ('address', models.TextField()),
                ('parent_name', models.CharField(max_length=100)),
                ('parent_phone', models.CharField(max_length=20)),
                ('parent_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('admission_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_assigned', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='students.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='schools.school')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAttendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_present', models.BooleanField(default=True)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='students.student')),
            ],
            options={
                'unique_together': {('student', 'date')},
            },
        ),
    ]
