from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from uuid import uuid4

from .validators import validate_phone_number


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number], blank=True, null=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.first_name
    
    @property
    def full_name(self):
        return self.get_full_name()


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    
    preferred_payment_method = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f'Profile of {self.user.email}'
    

class EmailVerification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='email_verifications'
    )

    token = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False
    )
    is_used = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField('Действителен до')
    
    class Meta:
        db_table = 'email_verifications'
        verbose_name = 'Подтверждение электронной почты'
        verbose_name_plural = 'Подтверждения электронной почты'
    
    def __str__(self):
        return f'EmailVerification for {self.user.email} - {"Used" if self.is_used else "Unused"}'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            timeout = getattr(settings, 'EMAIL_VERIFICATION_TIMEOUT', 86400)
            self.expires_at = timezone.now() + timedelta(seconds=timeout)
        super().save(*args, **kwargs)
        
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


class PasswordReset(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='password_resets'
    )
    token = models.UUIDField(
        default=uuid4,
        unique=True,
        editable=False
    )
    is_used = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField('Действителен до')
    
    class Meta:
        db_table = 'password_resets'
        verbose_name = 'Сброс пароля'
        verbose_name_plural = 'Сбросы паролей'
    
    def __str__(self):
        return f'PasswordReset for {self.user.email} - {"Used" if self.is_used else "Unused"}'
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            timeout = getattr(settings, 'PASSWORD_RESET_TIMEOUT', 3600)
            self.expires_at = timezone.now() + timedelta(seconds=timeout)
        super().save(*args, **kwargs)
        
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired
