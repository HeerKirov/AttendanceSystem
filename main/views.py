from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from . import models
from . import serializer
from . import utils
from rest_framework import mixins, generics
from rest_framework import viewsets, status
from . import permission as permissions
from rest_framework.response import Response
from rest_framework.filters import DjangoFilterBackend, OrderingFilter, SearchFilter
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .authority import has_auth, AuthorityName, all_auth, add_auth, belong_to
from django.contrib.auth.models import User as defaultUser
import json
import time

# Create your views here.


@csrf_exempt
def index(request):
    if request.method == 'GET':
        return render(request, 'homepage.html', {'content': "Welcome to Attendance System."})
    elif request.method == 'POST':
        js = json.loads(request.body)
        username = js['username']
        password = js['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                return HttpResponse(r'Authenticate success.', status=200)
            else:
                return HttpResponse(r'This user is not active.', status=401)
        else:
            return HttpResponse(r'Invalid login data.', status=401)


def auth(request, pk):  # 这个是获得/修改权限所使用的API视图。已经弃用。
    if not request.user.is_authenticated:
        return HttpResponse('Unauthorized.', status=401)
    auth_model = request.user.authority
    if not has_auth(auth_model.auth, AuthorityName.Root):
        return HttpResponse('Permission Denied.', status=403)
    users = defaultUser.objects.filter(username=pk).first()
    if users is None:
        return HttpResponse('User is not exists.', status=404)
    if request.method == 'GET':
        auth_set = all_auth(auth_model.auth)
        return HttpResponse(json.dumps(auth_set))
    elif request.method == 'POST':
        auth_set = json.loads(request.body)
        auth_number = 0
        add_auth(auth_number, auth_set)
        auth_model.auth = auth_number
        auth_model.save()
    else:
        return HttpResponse('Method Not Allowed', status=405)


def timetable_now(request):
    if request.method == 'GET':
        (now_year, now_month, now_day, now_hour, now_minute, now_second, _, _, _) = time.localtime(time.time())
        time_str = utils.datetime_to_str(now_year, now_month, now_day, now_hour, now_minute, now_second)
        return HttpResponse(time_str, status=200)
    else:
        return HttpResponse('Method Not Allowed', status=405)


def timetable_schedule(request):
    if request.method == 'GET':
        (now_year, now_month, now_day, now_hour, now_minute, now_second, _, _, _) = time.localtime(time.time())
        date_now = utils.date_to_str(now_year, now_month, now_day)
        schedules = models.SystemSchedule.objects.filter(begin__lte=date_now).filter(end__gte=date_now)
        if schedules:
            schedule = schedules.first()
            items = models.SystemScheduleItem.objects.filter(system_schedule=schedule).order_by('no')
            data = {
                'begin': utils.date_to_str(schedule.begin.year, schedule.begin.month, schedule.begin.day),
                'end': utils.date_to_str(schedule.end.year, schedule.end.month, schedule.end.day),
                'items': [
                    {
                        'begin': utils.time_to_str(item.begin.hour, item.begin.minute, item.begin.second),
                        'end': utils.time_to_str(item.end.hour, item.end.minute, item.end.second),
                        'no': item.no,
                    } for item in items
                ]
            }
            json_data = json.dumps(data)
            return HttpResponse(json_data, status=200)
        else:
            return HttpResponse('', status=200)
    else:
        return HttpResponse('Method Not Allowed', status=405)


class AuthAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):  # 现用的权限API
    queryset = models.Authority.objects.all()
    serializer_class = serializer.AuthoritySerializer
    permission_classes = (permissions.Action.AuthorityPermission,)
    lookup_field = 'id__username'


class PasswordAPIView(mixins.UpdateModelMixin, viewsets.GenericViewSet):  # 修改密码的API
    queryset = defaultUser.objects.all()
    serializer_class = serializer.PasswordSerializer
    lookup_field = 'username'


class PasswordAdminAPIView(mixins.UpdateModelMixin, viewsets.GenericViewSet):  # 管理员使用的修改密码的API
    queryset = defaultUser.objects.all()
    serializer_class = serializer.PasswordAdminSerializer
    permission_classes = (permissions.Action.PasswordAdminPermission,)
    lookup_field = 'username'


class UserViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserSerializer
    permission_classes = (permissions.User.UserPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('name', 'gender')
    ordering_fields = ('id', 'name', 'gender')
    search_fields = ('name',)
    lookup_field = 'username'


class UserDetailViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserDetailSerializer
    permission_classes = (permissions.User.UserDetailPermission,)
    lookup_field = 'username'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = getattr(instance, 'id')
        if user is not None:
            user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class StudentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsStudent.objects.all()
    serializer_class = serializer.StudentSerializer
    permission_classes = (permissions.User.StudentPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('classs', 'course_set')
    ordering_fields = ('id', 'username', 'classs')
    search_fields = ('username',)
    lookup_field = 'username'


class StudentDetailViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    queryset = models.AsStudent.objects.all()
    serializer_class = serializer.StudentDetailSerializer
    permission_classes = (permissions.User.StudentDetailPermission,)
    lookup_field = 'username'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = getattr(instance, 'id')
        if user is not None:
            user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TeacherViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsTeacher.objects.all()
    serializer_class = serializer.TeacherSerializer
    permission_classes = (permissions.User.TeacherPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('course_set',)
    ordering_fields = ('id', 'username',)
    search_fields = ('username',)
    lookup_field = 'username'


class TeacherDetailViewSet(mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    queryset = models.AsTeacher.objects.all()
    serializer_class = serializer.TeacherDetailSerializer
    permission_classes = (permissions.User.TeacherDetailPermission,)
    lookup_field = 'username'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = getattr(instance, 'id')
        if user is not None:
            user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InstructorViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsInstructor.objects.all()
    serializer_class = serializer.InstructorSerializer
    permission_classes = (permissions.User.InstructorPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('classs_set',)
    ordering_fields = ('id', 'username')
    search_fields = ('username',)
    lookup_field = 'username'


class InstructorDetailViewSet(mixins.RetrieveModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              viewsets.GenericViewSet):
    queryset = models.AsInstructor.objects.all()
    serializer_class = serializer.InstructorDetailSerializer
    permission_classes = (permissions.User.InstructorDetailPermission,)
    lookup_field = 'username'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = getattr(instance, 'id')
        if user is not None:
            user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClasssViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Classs.objects.all()
    serializer_class = serializer.ClasssSerializer
    permission_classes = (permissions.Item.ClasssPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('college', 'major', 'grade', 'number', 'as_instructor_set__username')
    ordering_fields = ('college', 'major', 'grade', 'number')
    search_fields = ('id', 'college', 'major')
    lookup_field = 'pk'


class ClasssDetailViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = models.Classs.objects.all()
    serializer_class = serializer.ClasssSerializer
    permission_classes = (permissions.Item.ClasssDetailPermission,)


class CourseBasicViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseBasicSerializer
    permission_classes = (permissions.Item.CourseBasicPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('name', 'teacher__username')
    ordering_fields = ('id', 'name', 'teacher')
    search_fields = ('id', 'name', 'teacher')


class CourseBasicDetailViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseBasicSerializer
    permission_classes = (permissions.Item.CourseBasicDetailPermission,)


class CourseManageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.CourseManage.objects.all()
    serializer_class = serializer.CourseManageSerializer
    permission_classes = (permissions.Item.CourseManagePermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id',)
    search_fields = ('id',)


class CourseManageDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.CourseManage.objects.all()
    serializer_class = serializer.CourseManageSerializer
    permission_classes = (permissions.Item.CourseManageDetailPermission,)


class ClassroomBasicViewSet(viewsets.ModelViewSet):
    queryset = models.Classroom.objects.all()
    serializer_class = serializer.ClassroomBasicSerializer
    permission_classes = (permissions.Item.ClassroomPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('name', 'size')
    ordering_fields = ('id', 'name', 'size')
    search_fields = ('id', 'name',)


class ClassroomManageBasicViewSet(mixins.ListModelMixin,
                                  mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  viewsets.GenericViewSet):
    queryset = models.ClassroomManage.objects.all()
    serializer_class = serializer.ClassroomManageSerializer
    permission_classes = (permissions.Item.ClassroomManagePermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id',)
    search_fields = ('id',)


class ExchangeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.ExchangeRecord.objects.all()
    serializer_class = serializer.ExchangeSerializer
    permission_classes = (permissions.Record.ExchangeRecordPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('course',)
    ordering_fields = ('id', 'course', 'approved')
    search_fields = ('id', 'course', 'approved')


class ExchangeDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.ExchangeRecord.objects.all()
    serializer_class = serializer.ExchangeSerializer
    permission_classes = (permissions.Record.ExchangeDetailRecordPermission,)


class ExchangeApplyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.ExchangeRecord.objects.all()
    serializer_class = serializer.ExchangeApplySerializer
    permission_classes = (permissions.Record.ExchangeApplyPermission,)


class ExchangeApproveViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.ExchangeRecord.objects.all()
    serializer_class = serializer.ExchangeApproveSerializer
    permission_classes = (permissions.Record.ExchangeApprovePermission,)


class LeaveViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.LeaveRecord.objects.all()
    serializer_class = serializer.LeaveSerializer
    permission_classes = (permissions.Record.LeaveRecordPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('student__username',)
    ordering_fields = ('id', 'student', 'approved')
    search_fields = ('id', 'student', 'approved')


class LeaveDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.LeaveRecord.objects.all()
    serializer_class = serializer.LeaveSerializer
    permission_classes = (permissions.Record.LeaveDetailRecordPermission,)


class LeaveApplyViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.LeaveRecord.objects.all()
    serializer_class = serializer.LeaveApplySerializer
    permission_classes = (permissions.Record.LeaveApplyPermission,)


class LeaveApproveViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.LeaveRecord.objects.all()
    serializer_class = serializer.LeaveApproveSerializer
    permission_classes = (permissions.Record.LeaveApprovePermission,)


class ClassroomRecordViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.ClassroomRecord.objects.all()
    serializer_class = serializer.ClassroomRecordSerializer
    permission_classes = (permissions.Record.ClassroomRecordPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('student__username', 'classroom_manage')
    ordering_fields = ('id', 'student', 'classroom_manage')
    search_fields = ('id', 'student', 'classroom_manage')


class ClassroomRecordDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.ClassroomRecord.objects.all()
    serializer_class = serializer.ClassroomRecordSerializer
    permission_classes = (permissions.Record.ClassroomRecordDetailPermission,)


class ClassroomCheckViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.ClassroomRecord.objects.all()
    serializer_class = serializer.ClassroomCheckSerializer


class CourseScheduleViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.CourseSchedule.objects.all()
    serializer_class = serializer.CourseScheduleSerializer
    permission_classes = (permissions.Record.CourseSchedulePermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('classroom', 'course', 'year', 'term')
    ordering_fields = ('id', 'year', 'term', 'classroom', 'course')
    search_fields = ('id', 'year', 'term', 'classroom', 'course')


class CourseScheduleDetailViewSet(mixins.RetrieveModelMixin,
                                  mixins.UpdateModelMixin,
                                  mixins.DestroyModelMixin,
                                  viewsets.GenericViewSet):
    queryset = models.CourseSchedule.objects.all()
    serializer_class = serializer.CourseScheduleSerializer
    permission_classes = (permissions.Record.CourseScheduleDetailPermission,)


class AttendanceRecordViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AttendanceRecord.objects.all()
    serializer_class = serializer.AttendanceRecordSerializer
    permission_classes = (permissions.Record.AttendanceRecordPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('student__username', 'course_manage')
    ordering_fields = ('id', 'date', 'status', 'student', 'course_manage')
    search_fields = ('id', 'date', 'status', 'student', 'course_manage')


class AttendanceRecordDetailViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = models.AttendanceRecord.objects.all()
    serializer_class = serializer.AttendanceRecordSerializer
    permission_classes = (permissions.Record.AttendanceRecordDetailPermission,)


class SystemScheduleViewSet(viewsets.ModelViewSet):
    queryset = models.SystemSchedule.objects.all()
    serializer_class = serializer.SystemScheduleSerializer
    permission_classes = (permissions.Schedule.SystemSchedulePermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id',)
    search_fields = ('id',)


class SystemScheduleItemViewSet(viewsets.ModelViewSet):
    queryset = models.SystemScheduleItem.objects.all()
    serializer_class = serializer.SystemScheduleItemSerializer
    permission_classes = (permissions.Schedule.SystemScheduleItemPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filter_fields = ('system_schedule',)
    ordering_fields = ('id', 'system_schedule')
    search_fields = ('id', 'system_schedule')


