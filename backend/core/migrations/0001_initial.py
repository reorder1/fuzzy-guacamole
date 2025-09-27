from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_number', models.CharField(max_length=50)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('batch', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='students', to='core.batch')),
            ],
            options={
                'ordering': ['student_number'],
            },
        ),
        migrations.AddConstraint(
            model_name='student',
            constraint=models.UniqueConstraint(fields=('batch', 'student_number'), name='unique_student_per_batch'),
        ),
    ]
