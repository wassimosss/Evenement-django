from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager, Group, Permission
# Create your models here.
class UtilisateurManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        extra_fields.setdefault("role", "client")
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")  
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(username, email, password, **extra_fields)
class Utilisateur(AbstractUser):
    email = models.EmailField(unique=True)
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('client', 'client'),  
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='client')
    groups = models.ManyToManyField(Group, related_name="client_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="client_permissions", blank=True)
    objects = UtilisateurManager()
    def __str__(self):
        return self.username
class Profile(models.Model):
    user=models.OneToOneField(Utilisateur, on_delete=models.CASCADE)
    bio=models.TextField(blank=True,null=True)
    phone_number=models.CharField(max_length=15, blank=True)
    address=models.CharField(max_length=255, blank=True)
    image=models.ImageField(upload_to='profils_photos/', blank=True, null=True, default='profils_photos/default.jpeg')