"""
URL configuration for DjangoMinio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

# from DjangoMinio import views


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('upload/', views.upload_file, name= 'upload_file'),
#     path('download/<str:filename>/', views.download_file, name= 'download_file'),
#     path('upload_file/', views.upload_file, name= 'upload_file'),
#     path('create_bucket/', views.create_bucket, name= 'create_bucket'),
#     path('list_buckets/', views.list_buckets, name= 'list_buckets'),
#     path('list_objects/', views.list_objects, name= 'list_objects'),
# ]

from .views import FilesView, BucketsView, ObjectsView

urlpatterns = [
    path('file/', FilesView.as_view(), name='file_view'),
    path('bucket/', BucketsView.as_view(), name='bucket_view'),
    path('object/', ObjectsView.as_view(), name='object_view'),
]
