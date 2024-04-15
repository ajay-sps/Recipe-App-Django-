from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


class Roles(models.Model):
    name = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.name


class User(AbstractUser):
    roles = models.ForeignKey(
        Roles, on_delete=models.PROTECT, null=True, default=2)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.PROTECT, related_name='userprofile')
    profession = models.CharField(max_length=255, null=True, blank=True)
    profilePic = models.ImageField(
        upload_to='static/profilepic', null=True, blank=True ,default='static/profilepic/default_profile.png')
    verification_code = models.CharField(max_length=100, null=True)
    phone = models.BigIntegerField(null=True, blank=True)
    about = models.CharField(max_length=555, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zip = models.TextField(null=True, blank=True)
