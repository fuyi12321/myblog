"""MyBlog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls.py/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls.py import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls.py'))
"""
# from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls.py),
    path('', include('news.urls')),
    path('user/', include('users.urls')),
    path('', include('verifications.urls')),
    path('doc/', include('doc.urls')),
    path('course/', include('course.urls')),
    path('admin/', include('admin.urls'))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
