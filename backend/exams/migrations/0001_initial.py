from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('num_items', models.PositiveIntegerField(default=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='exams', to='core.batch')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ExamSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_code', models.CharField(max_length=10)),
                ('answer_key', models.JSONField(default=list)),
                ('exam', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='sets', to='exams.exam')),
            ],
            options={
                'ordering': ['set_code'],
                'unique_together': {('exam', 'set_code')},
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set_code', models.CharField(max_length=10)),
                ('raw_score', models.PositiveIntegerField(default=0)),
                ('percent', models.FloatField(default=0.0)),
                ('breakdown', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('exam', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='scores', to='exams.exam')),
                ('student', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='scores', to='core.student')),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='score',
            constraint=models.UniqueConstraint(fields=('exam', 'student'), name='unique_exam_student_score'),
        ),
    ]
