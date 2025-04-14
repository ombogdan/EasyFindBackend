# myapp/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings

class ClientUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Користувач повинен мати електронну пошту')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class ClientUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10, choices=[('user', 'User'), ('admin', 'Admin')])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = ClientUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

class OrganizationOwner(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.user.is_staff:
            self.user.is_staff = True
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email

class Organization(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='organization_images/', blank=True, null=True)
    owner = models.ForeignKey(OrganizationOwner, on_delete=models.CASCADE, related_name='organizations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    address = models.CharField(max_length=500)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class WorkingHours(models.Model):
    DAYS_OF_WEEK = [
        ('mon', 'Понеділок'),
        ('tue', 'Вівторок'),
        ('wed', 'Середа'),
        ('thu', 'Четвер'),
        ('fri', 'Пʼятниця'),
        ('sat', 'Субота'),
        ('sun', 'Неділя'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='working_hours')
    day = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.organization.name} - {self.get_day_display()}"

    class Meta:
        unique_together = ('organization', 'day')

class ServiceType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='services'
    )

    def __str__(self):
        return self.name
class Employee(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)

    organizations = models.ManyToManyField('Organization', related_name='employees')  # 🔥 зміна тут

    service_types = models.ManyToManyField(ServiceType, related_name='employees')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
