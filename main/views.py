from django.shortcuts import render
from . import models
from . import serializer
from rest_framework import mixins,generics
from rest_framework import viewsets
from . import permission as permissions
from .authority import AuthorityName
from .authority import has_auth, belong_to, belong_to_side
from rest_framework.filters import DjangoFilterBackend, OrderingFilter, SearchFilter

# Create your views here.


def check_on(request):
    pass


def adduser(request):
    pass


def removeuser(request):
    pass


def auth(request, pk):
    pass


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


class UserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserSerializer
    permission_classes = (permissions.User.UserPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    # filter_fields = ('name', 'gender')
    ordering_fields = ('id', 'name', 'gender')
    search_fields = ('name',)
    lookup_field = 'username'


class UserViewDetailSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializer.UserSerializer
    permission_classes = (permissions.User.UserDetailPermission,)
    lookup_field = 'username'


class StudentViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = models.AsStudent.objects.all()
    serializer_class = serializer.StudentSerializer
    permission_classes = (permissions.User.StudentPermission,)
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    ordering_fields = ('id', 'classs')
    search_fields = ('classs',)
    lookup_field = 'username'


class StudentDetailViewset(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = models.AsStudent.objects.all()
    serializer_class = serializer.StudentSerializer
    permission_classes = (permissions.User.StudentDetailPermission,)
    lookup_field = 'username'







