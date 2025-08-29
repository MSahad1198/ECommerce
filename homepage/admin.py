from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer
from .models import Product

class CustomerAdmin(UserAdmin):
    model = Customer
    list_display = ('email', 'username', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_active')}
        ),
    )
    list_display = ('username', 'email', 'is_staff')

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Product)