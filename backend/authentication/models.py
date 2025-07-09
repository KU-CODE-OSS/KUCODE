from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    firebase_uid = models.CharField(max_length=255, unique=True, null=True, blank=True)
    korea_email = models.EmailField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username or self.email