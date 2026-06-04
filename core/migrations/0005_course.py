# Generated migration for Course model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_student_department_alter_student_enrollment_no'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(help_text='e.g., PHY111, MTH201', max_length=20)),
                ('name', models.CharField(help_text='e.g., Physics 1, Calculus 2', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Optional course description', null=True)),
                ('credits', models.IntegerField(default=3, help_text='Number of credit units')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='core.department')),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
                'ordering': ['department', 'code'],
            },
        ),
        migrations.AddConstraint(
            model_name='course',
            constraint=models.UniqueConstraint(fields=['department', 'code'], name='unique_department_code'),
        ),
    ]
