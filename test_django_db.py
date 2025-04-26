import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'macro_pulse.settings')
django.setup()

print("Django Database Settings:")
print(f"NAME: {settings.DATABASES['default']['NAME']}")
print(f"USER: {settings.DATABASES['default']['USER']}")
print(f"PASSWORD: {settings.DATABASES['default']['PASSWORD']}")
print(f"HOST: {settings.DATABASES['default']['HOST']}")
print(f"PORT: {settings.DATABASES['default']['PORT']}") 