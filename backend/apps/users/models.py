from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedUUIDModel
from apps.users.managers import UserManager


class User(TimeStampedUUIDModel, AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "Admin", "Admin"
        MANAGER = "Manager", "Manager"
        ENGINEER = "Engineer", "Engineer"
        EXPERT = "Expert", "Expert"
        CLIENT = "Client", "Client"

    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.ENGINEER)
    is_blocked = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.email

