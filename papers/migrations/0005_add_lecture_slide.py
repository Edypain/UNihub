from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0004_add_course_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='LectureSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('course_code', models.CharField(default='', help_text='Course code like PHY111', max_length=10, blank=True)),
                ('slide_file', models.FileField(upload_to='slides/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('department', models.ForeignKey(on_delete=models.CASCADE, to='core.department')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, to='auth.user')),
            ],
        ),
    ]
