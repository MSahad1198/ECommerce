from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django import forms

UserModel = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate customers using their email address (non-admin routes only).
    Falls back to default username backend for admin.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Only run on non-admin pages
        if request and request.path.startswith('/admin/'):
            return None

        if username is None or password is None:
            return None

        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None


class UsernameAdminAuthenticationForm(AuthenticationForm):
    """
    Forces the Django admin login form to display 'Username' instead of 'Email'.
    """
    username = forms.CharField(label="Username")


class MyAdminSite(AdminSite):
    """
    Custom AdminSite that uses a username label on login form.
    """
    login_form = UsernameAdminAuthenticationForm


# Create a reusable instance of the custom AdminSite
admin_site = MyAdminSite()
