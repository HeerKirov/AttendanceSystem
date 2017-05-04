from . import models
from rest_framework import serializers
from django.contrib.auth.models import User as defaultUser


class UserSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = models.User
        fields = ('id', 'name', 'gender', 'register_time', 'last_login_time',)


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    classs = serializers.PrimaryKeyRelatedField(queryset=models.Classs.objects.all())
    course_set = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all(), many=True)

    class Meta:
        model = models.AsStudent
        fields = ('id', 'classs', 'course_set')
        read_only_fields = ('username',)

