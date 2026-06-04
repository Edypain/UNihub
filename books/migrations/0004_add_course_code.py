from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_alter_book_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='course_code',
            field=models.CharField(blank=True, default='', help_text='Course code like PHY111', max_length=10),
        ),
    ]
