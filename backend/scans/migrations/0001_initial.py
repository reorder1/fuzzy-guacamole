from django.db import migrations, models
import django.db.models.deletion

import scans.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('exams', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Scan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=scans.models.scan_upload_path)),
                ('extracted_student_number', models.CharField(blank=True, max_length=50)),
                ('extracted_set_code', models.CharField(blank=True, max_length=10)),
                ('answers', models.JSONField(blank=True, default=list)),
                ('confidence', models.FloatField(default=0.0)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processed', 'Processed'), ('needs_review', 'Needs Review')], default='pending', max_length=20)),
                ('issues', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='exams.exam')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='scans', to='core.student')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
