from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from . import models
from . import serializer
from rest_framework import mixins, generics
from rest_framework import viewsets
from . import permission as permissions
from rest_framework.filters import DjangoFilterBackend, OrderingFilter, SearchFilter
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from .authority import has_auth, AuthorityName, all_auth, add_auth
from django.contrib.auth.models import User as defaultUser
import json

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
            return HttpResponse(r'Valid login data.', status=401)


def check_on(request):
    pass


def adduser(request):
    pass


def removeuser(request):
    pass


def auth(request, pk):
    if not request.user.is_authenticated:
        return HttpResponse('Permission Denied.', status=403)
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


def exchange_approve(request):
    pass


def exchange_apply(request):
    pass


def leave_approve(request):
    pass


def leave_apply(request):
    pass


def timetable_now(request):
    pass


def timetable_datetable(request):
    pass


class AuthAPIView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.Authority.objects.all()
    serializer_class = serializer.AuthoritySerializer
    permission_classes = (permissions.Action.AuthorityPermision,)
    lookup_field = 'id__username'


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserSerializer
    # authentication_classes = (BasicAuthentication,)
    # authentication_classes = (BasicAuthentication, SessionAuthentication, )
    permission_classes = (permissions.User.UserPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    # filter_fields = ('name', 'gender')
    ordering_fields = ('id', 'name', 'gender')
    search_fields = ('name',)
    lookup_field = 'username'


class UserViewDetailSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserSerializer
    # authentication_classes = (BasicAuthentication,)
    # authentication_classes = (BasicAuthentication, SessionAuthentication,)
    permission_classes = (permissions.User.UserDetailPermission,)
    lookup_field = 'username'


class StudentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AsStudent.objects.all()
    serializer_class = serializer.StudentSerializer
    permission_classes = (permissions.User.StudentPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'username', 'classs')
    search_fields = ('username',)
    lookup_field = 'username'


class StudentDetailViewset(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsStudent.objects.all()
    serializer_class = serializer.StudentSerializer
    permission_classes = (permissions.User.StudentDetailPermission,)
    lookup_field = 'username'


class TeacherViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AsTeacher.objects.all()
    serializer_class = serializer.TeacherSerializer
    permission_classes = (permissions.User.TeacherPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'username',)
    search_fields = ('username',)
    lookup_field = 'username'


class TeacherDetailViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsTeacher.objects.all()
    serializer_class = serializer.TeacherSerializer
    permission_classes = (permissions.User.TeacherDetailPermission,)
    lookup_field = 'username'


class InstructorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AsInstructor.objects.all()
    serializer_class = serializer.InstructorSerializer
    permission_classes = (permissions.User.InstructorPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'username')
    search_fields = ('username',)
    lookup_field = 'username'


class InstructorDetailViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsInstructor.objects.all()
    serializer_class = serializer.InstructorSerializer
    permission_classes = (permissions.User.InstructorDetailPermission,)
    lookup_field = 'username'


class ClasssViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = models.Classs.objects.all()
    serializer_class = serializer.ClasssSerializer
    permission_classes = (permissions.Item.ClasssPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('college', 'major', 'grade', 'number')
    search_fields = ('id', 'college', 'major', 'as_instructor_set__username')
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
    ordering_fields = ('id', 'name', 'teacher__username')
    search_fields = ('id', 'name', 'teacher__username')


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







