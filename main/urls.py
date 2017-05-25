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
from rest_framework import routers


r = DefaultRouter()
r.register(r'action/auth', views.AuthAPIView)
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
r.register(r'classroom/basic', views.ClassroomBasicViewSet)
r.register(r'classroom/manage', views.ClassroomManageBasicViewSet)
r.register(r'exchange/exchange', views.ExchangeViewSet)
r.register(r'exchange/exchange', views.ExchangeDetailViewSet)
r.register(r'exchange/exchange-operator', views.ExchangeApplyViewSet, base_name='exchange-operator')
r.register(r'exchange/exchange-operator', views.ExchangeApproveViewSet, base_name='exchange-operator')
r.register(r'exchange/leave', views.LeaveViewSet)
r.register(r'exchange/leave', views.LeaveDetailViewSet)
r.register(r'exchange/leave-operator', views.LeaveApplyViewSet, base_name='leave-operator')
r.register(r'exchange/leave-operator', views.LeaveApproveViewSet, base_name='leave-operator')
r.register(r'record/classroom-record', views.ClassroomRecordViewSet)
r.register(r'record/classroom-record', views.ClassroomRecordDetailViewSet)
r.register(r'record/classroom-operator', views.ClassroomCheckViewSet, base_name='classroom-operator')
r.register(r'record/course-schedule', views.CourseScheduleViewSet)
r.register(r'record/course-schedule', views.CourseScheduleDetailViewSet)
r.register(r'record/attendance-record', views.AttendanceRecordViewSet)
r.register(r'record/attendance-record', views.AttendanceRecordDetailViewSet)
r.register(r'schedule/system-schedule', views.SystemScheduleViewSet)
r.register(r'schedule/system-schedule-item', views.SystemScheduleItemViewSet)

urlpatterns = [
    url(r'^', include(r.urls)),
]

urlpatterns_action = [
    url(r'^now', views.timetable_now)
]
