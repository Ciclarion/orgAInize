from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('pro', 'Pro'),
        ('apprenant', 'Apprenant'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='apprenant')
    
    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set', blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Ajoutez d'autres champs spécifiques aux profils si nécessaire
    
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)  # 'User' or 'Bot'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
