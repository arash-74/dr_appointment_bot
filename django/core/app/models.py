from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django_jalali.db.models import jManager,jDateTimeField,jDateField
from jdatetime import datetime


class UserManager(BaseUserManager):
    def create_user(self, username=None, chat_id=None, password=None, **extra_fields):
        if not username and not chat_id:
            raise ValueError('Users must have username or chat_id')
        user = None
        if not chat_id and username == 'admin':
            user = self.model(username=username, password=password, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
        elif not username and chat_id:
            user = self.model(chat_id=chat_id, **extra_fields)
            user.set_unusable_password()
            user.save(using=self._db)

        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        return self.create_user(username=username, password=password, **extra_fields)


class User(PermissionsMixin, AbstractBaseUser):
    username = models.CharField(unique=True, null=True, blank=True)
    chat_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username if self.username else str(self.chat_id)


class Appointment(models.Model):
    objects = jManager()
    from_date = jDateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='bookings',blank=True,null=True)
    is_booking = models.BooleanField(default=False)
    booking_date = jDateField(null=True,blank=True)
    price = models.IntegerField()
    
    def save(self,*args,**kwargs):
        if self.user:
            self.is_booking = True
        else:
            self.is_booking = False
        super().save(*args,**kwargs)