from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    #  Custom logout before anything else
   # path('site-logout/', auth_views.LogoutView.as_view(), name='site_logout'),
    #  path('logout/', auth_views.LogoutView.as_view(), name='logout'),
   #h('site-logout/', auth_views.LogoutView.as_view(), name='site_logout'),

    # Homepage app URLs
    path('', include('homepage.urls')),
]
