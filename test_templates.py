import os
import django
from django.conf import settings
from django.template import loader

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fitnessmaster.settings')
django.setup()

try:
    tmpl = loader.get_template('index.html')
    print(f"Template Name: {tmpl.template.name}")
    print("Template Source: Found")
except Exception as e:
    print(f"Error: {e}")
