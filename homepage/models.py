# homepage/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings

# ------------------------------
# Product model
# ------------------------------
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Meat', 'Meat'),
        ('Fish', 'Fish'),
        ('Veggies', 'Veggies'),
        ('Grocery', 'Grocery'),
        ('Fruit', 'Fruit')
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.URLField(blank=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Grocery')

    def __str__(self):
        return self.name


# ------------------------------
# Customer model
# ------------------------------
class CustomerManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Customers must have an email address")
        email = self.normalize_email(email)
        customer = self.model(email=email, **extra_fields)
        customer.set_password(password)
        customer.save(using=self._db)
        return customer

    def create_superuser(self, email, password=None, **extra_fields):
        raise ValueError("Use Django's admin User model for admin accounts.")


class Customer(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Avoid group/permission conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customer_set',
        blank=True,
        help_text='The groups this customer belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customer_permissions_set',
        blank=True,
        help_text='Specific permissions for this customer.',
        verbose_name='user permissions'
    )

    objects = CustomerManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
           

