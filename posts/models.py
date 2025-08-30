from django.db import models
import random

def get_filename_ext(filepath):
    pass

def upload_image_path(instance, filename):
    new_filename = random.randint(1, 151251251)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    
    return f"post_images/{new_filename}/{final_filename}".format(new_filename=new_filename, final_filename=final_filename)
# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200, blank=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to=upload_image_path, blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.user.username} on {self.created_at}"