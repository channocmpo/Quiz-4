from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
import os
import random
def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext

def upload_image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    new_filename = f"{random.randint(100000, 999999)}{ext}"
    return f"profile_pictures/{instance.user.username}/{new_filename}"

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, is_active=True, is_staff=False, is_admin=False):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')

        user_obj = self.model(
            email = self.normalize_email(email)
        )
        user_obj.username = username
        user_obj.set_password(password)  # Hash the password
        user_obj.active = is_active
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.save(using=self._db)

        return user_obj

    def create_staffuser(self, email,username, password=None):
        user = self.create_user(email,username, password, is_staff=True, is_active=True)
        return user

    def create_superuser(self, email,username, password=None):
        user = self.create_user(
            email,
            username,
            password=password,
            is_staff=True,
            is_admin=True,
            is_active=True
        )
        return user

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=150, unique=True, blank=False)
    staff = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.admin
    



class Profile(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to=upload_image_path, blank=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email