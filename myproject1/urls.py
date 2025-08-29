from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from homepage import views  # Import your custom views
from django.urls import path, include     # ✅ import include so it works
from homepage.backends import admin_site  # import the custom admin instance



urlpatterns = [
    path('admin/', admin.site.urls),

    #  Custom logout before anything else
    path('site-logout/', views.site_logout, name='site_logout'),  # Use your custom logout
      
    path('logout/', views.site_logout, name='logout'),  # Optionally add this
    # Homepage app URLs
    path('', include('homepage.urls')),
    path('admin/', admin_site.urls),          # use custom admin
    path('', include('homepage.urls')),       # customer site routes
]
