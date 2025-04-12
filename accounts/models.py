from django.db import models
from django.contrib.postgres.fields import ArrayField 

class User(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password_hash = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    cnic = models.CharField(max_length=15, unique=True)
    status = models.BooleanField(default=True)
    user_image = models.ImageField(upload_to='user_images/', blank=True, null=True)
    face_encoding = ArrayField(models.FloatField(), null=True, blank=True)
    def __str__(self):
        return self.username

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.user.username} - {'Active' if self.is_active else 'Inactive'}"



class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)