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
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = models.AsStudent
        fields = ('id', 'user', 'classs', 'course_set')
        read_only_fields = ('username',)


class TeacherSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)
    course_set = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all(), many=True)

    class Meta:
        model = models.AsTeacher
        fields = ('id', 'user', 'course_set')
        read_only_fields = ('username',)


class InstructorSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    classs_set = serializers.PrimaryKeyRelatedField(queryset=models.Classs.objects.all(), many=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = models.AsInstructor
        fields = ('id', 'user', 'classs_set')
        read_only_fields = ('username',)


class ClasssSerializer(serializers.ModelSerializer):
    as_student_set = serializers.SlugRelatedField(
        slug_field='username', queryset=models.AsStudent.objects.all(), many=True)
    as_instructor_set = serializers.SlugRelatedField(
        slug_field='username', queryset=models.AsInstructor.objects.all(), many=True)

    class Meta:
        model = models.Classs
        fields = ('id', 'grade', 'college', 'major', 'number', 'as_instructor_set', 'as_student_set')


class CourseBasicSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(slug_field='username', queryset=models.AsTeacher.objects.all())
    as_student_set = serializers.SlugRelatedField(
        slug_field='username', queryset=models.AsStudent.objects.all(), many=True)
    course_schedule_set = serializers.PrimaryKeyRelatedField(
        queryset=models.CourseSchedule.objects.all(), many=True)
    exchange_record_set = serializers.PrimaryKeyRelatedField(
        queryset=models.ExchangeRecord.objects.all(), many=True)

    def create(self, validated_data):
        # 需要在创建对象时同时创建管理信息。
        ins = super().create(validated_data)
        manage = models.CourseManage(id=ins)
        manage.save()
        return ins

    class Meta:
        model = models.Course
        fields = ('id', 'name', 'teacher', 'as_student_set', 'course_schedule_set', 'exchange_record_set')


class CourseManageSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all())
    attendance_record_set = serializers.PrimaryKeyRelatedField(
        queryset=models.AttendanceRecord.objects.all(), many=True)

    class Meta:
        model = models.CourseManage
        fields = ('id', 'attendance_record_set')
