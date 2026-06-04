import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Department

def seed_departments():
    departments = [
        {"name": "Computer Science & Engineering", "code": "CSE"},
        {"name": "Electrical & Electronics Engineering", "code": "EEE"},
        {"name": "Mechanical Engineering", "code": "ME"},
        {"name": "Civil Engineering", "code": "CE"},
        {"name": "Business Administration", "code": "BBA"},
        {"name": "Physics", "code": "PHY"},
        {"name": "Mathematics", "code": "MTH"},
    ]

    print("Seeding departments...")
    for dept in departments:
        obj, created = Department.objects.get_or_create(
            code=dept["code"], 
            defaults={"name": dept["name"]}
        )
        if created:
            print(f" - Created department: {dept['name']} ({dept['code']})")
        else:
            print(f" - Department already exists: {dept['name']} ({dept['code']})")
    print("Seeding complete.")

if __name__ == '__main__':
    seed_departments()
