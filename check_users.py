import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
print("Users in database:")
for user in User.objects.all():
    print(f"- {user.username} (Email: {user.email}, Staff: {user.is_staff})")
