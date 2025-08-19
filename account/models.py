from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
import uuid


class organization(models.Model):
    """
    Represents a client company using our platform.
    """

    id = models.UUIDField(primary_key= True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class UserManager(BaseUserManager):
    """
    Custom user manager to handle user creation. where email is the unique identifier
    """
    def create_user(self,email,password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        email = email.lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email,password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser',True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email,password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
        Custom user model for admin, recruiters and evaluators.
    """

    class Role(models.TextChoices):
        ADMIN = 'Admin', 'Admin'
        RECRUITER = 'Recruiter', 'Recruiter'
        EVALUATOR = 'Evaluator','Evaluator'
    
    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    organization = models.ForeignKey(organization, on_delete = models.CASCADE,related_name='users')
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default = False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD ='email'
    REQUIRED_FIELDS =['name','organization']

    def __str__(self):
        return self.email
