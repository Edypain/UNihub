from django.db import migrations
from django.contrib.auth.models import User

def add_student_profiles(apps, schema_editor):
    Student = apps.get_model('core', 'Student')
    for user in User.objects.all():
        Student.objects.get_or_create(user=user)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),  # adjust to your last core migration
    ]

    operations = [
        migrations.RunPython(add_student_profiles),
    ]