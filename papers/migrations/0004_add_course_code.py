from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0003_alter_pastpaper_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='pastpaper',
            name='course_code',
            field=models.CharField(blank=True, default='', help_text='Course code like PHY111', max_length=10),
        ),
    ]
