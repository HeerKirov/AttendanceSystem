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
r.register(r'user/auth', views.AuthAPIView)
r.register(r'user/password', views.PasswordAPIView, base_name='password-detail')
r.register(r'user/password-admin', views.PasswordAdminAPIView, base_name='password-admin-detail')
r.register(r'auth/users', views.UserViewSet)
r.register(r'auth/users', views.UserDetailViewSet)
r.register(r'auth/students', views.StudentViewSet)
r.register(r'auth/students', views.StudentDetailViewSet)
r.register(r'auth/teachers', views.TeacherViewSet)
r.register(r'auth/teachers', views.TeacherDetailViewSet)
r.register(r'auth/instructors', views.InstructorViewSet)
r.register(r'auth/instructors', views.InstructorDetailViewSet)
r.register(r'classes', views.ClasssViewSet)
r.register(r'classes', views.ClasssDetailViewSet)
r.register(r'courses/basic', views.CourseBasicViewSet)
r.register(r'courses/basic', views.CourseBasicDetailViewSet)
r.register(r'courses/manage', views.CourseManageViewSet)
r.register(r'courses/manage', views.CourseManageDetailViewSet)
r.register(r'classrooms/basic', views.ClassroomBasicViewSet)
r.register(r'classrooms/basic', views.ClassroomBasicDetailViewSet)
r.register(r'classrooms/manage', views.ClassroomManageBasicViewSet)
r.register(r'exchange/exchanges', views.ExchangeViewSet)
r.register(r'exchange/exchanges', views.ExchangeDetailViewSet)
r.register(r'exchange/exchanges-operator', views.ExchangeApplyViewSet, base_name='exchange-operator')
r.register(r'exchange/exchanges-operator', views.ExchangeApproveViewSet, base_name='exchange-operator')
r.register(r'exchange/leaves', views.LeaveViewSet)
r.register(r'exchange/leaves', views.LeaveDetailViewSet)
r.register(r'exchange/leaves-operator', views.LeaveApplyViewSet, base_name='leave-operator')
r.register(r'exchange/leaves-operator', views.LeaveApproveViewSet, base_name='leave-operator')
r.register(r'record/classroom-records', views.ClassroomRecordViewSet)
r.register(r'record/classroom-records', views.ClassroomRecordDetailViewSet)
r.register(r'record/classrooms-operator', views.ClassroomCheckViewSet, base_name='classroom-operator')
r.register(r'record/course-schedules', views.CourseScheduleViewSet)
r.register(r'record/course-schedules', views.CourseScheduleDetailViewSet)
r.register(r'record/attendance-records', views.AttendanceRecordViewSet)
r.register(r'record/attendance-records', views.AttendanceRecordDetailViewSet)
r.register(r'schedule/system-schedules', views.SystemScheduleViewSet)
r.register(r'schedule/system-schedule-items', views.SystemScheduleItemViewSet)

urlpatterns = [
    url(r'^', include(r.urls)),
]

urlpatterns_action = [
    url(r'self-authority', views.self_authority),
    url(r'^now', views.timetable_now),
    url(r'^schedule', views.timetable_schedule),
    url(r'belong', views.belong_check),
]
