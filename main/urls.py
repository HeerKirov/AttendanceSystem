"""AttendanceSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from . import views
from rest_framework.routers import DefaultRouter

r = DefaultRouter()
r.register(r'auth/users', views.UserViewSet)
r.register(r'auth/users', views.UserViewDetailSet)
r.register(r'auth/students', views.StudentViewSet)
r.register(r'auth/students', views.StudentDetailViewset)
r.register(r'auth/teachers', views.TeacherViewSet)
r.register(r'auth/teachers', views.TeacherDetailViewSet)
r.register(r'auth/instructors', views.InstructorViewSet)
r.register(r'auth/instructors', views.InstructorDetailViewSet)
r.register(r'class', views.ClasssViewSet)
r.register(r'class', views.ClasssDetailViewSet)
r.register(r'course/basic', views.CourseBasicViewSet)
r.register(r'course/basic', views.CourseBasicDetailViewSet)
r.register(r'course/manage', views.CourseManageViewSet)
r.register(r'course/manage', views.CourseManageDetailViewSet)

urlpatterns = [
    url(r'^', include(r.urls))
]



