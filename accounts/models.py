from django.db import models
from django.contrib.auth.models import User

# Create your models here.
# class User(AbstractUser):
#     photo = models.ImageField()
#     date_of_birth = models.DateField()
#     adress = models.CharField()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} profili"