from django.test import TestCase
from django.utils import timezone
from django.conf import settings

settings.configure()
print(timezone.now())
