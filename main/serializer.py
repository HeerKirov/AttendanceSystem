from . import models
from rest_framework import serializers
from . import authority
import time
from django.contrib.auth.models import User as defaultUser


class AuthoritySerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = models.Authority
        fields = ('id', 'auth')


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
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    attendance_record_set = serializers.PrimaryKeyRelatedField(
        queryset=models.AttendanceRecord.objects.all(), many=True)

    class Meta:
        model = models.CourseManage
        fields = ('id', 'attendance_record_set',)


class ClassroomBasicSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=30, write_only=True, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        # 需要在创建对象时同时创建管理信息。
        data = {
            'id': validated_data['id'],
            'name': validated_data['name'],
            'size': validated_data['size']
        }
        pw = validated_data['password']
        ins = super().create(data)
        manage = models.ClassroomManage(id=ins, password=pw)
        manage.save()
        return ins

    class Meta:
        model = models.Classroom
        fields = ('id', 'name', 'size', 'password')


class ClassroomManageSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = models.ClassroomManage
        fields = ('id', 'password',)


class ExchangeSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all())

    class Meta:
        model = models.ExchangeRecord
        fields = ('id', 'from_date', 'from_course_number',
                  'goal_date', 'goal_course_number',
                  'note', 'approved', 'course')


class ExchangeApplySerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all())

    def create(self, validated_data):
        user = self.context['request'].user
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError('Unauthorized.')
        profile = user.profile
        course = validated_data['course']
        if course is None:
            raise serializers.ValidationError('Course is not exists.')
        if not authority.belong_to(course, profile):
            raise serializers.ValidationError('Permission Denied.')
        validated_data['approved'] = 'approving'
        return super().create(validated_data)

    class Meta:
        model = models.ExchangeRecord
        fields = ('from_date', 'from_course_number',
                  'goal_date', 'goal_course_number',
                  'note', 'course')


class ExchangeApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.ExchangeRecord
        fields = ('id', 'approved')


class LeaveSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', queryset=models.AsStudent.objects.all())

    class Meta:
        model = models.LeaveRecord
        fields = ('id', 'time_begin', 'time_end', 'note', 'approved', 'student')


class LeaveApplySerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', queryset=models.AsStudent.objects.all())

    def create(self, validated_data):
        user = self.context['request'].user
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError('Unauthorized.')
        profile = user.profile  # 使用者的profile
        auth_number = getattr(profile, 'authority').auth  # 获得使用者账户的权限数字
        student = validated_data['student']  # 申请请假的目标学生
        if student is None:
            raise serializers.ValidationError('Student is not exists.')

        # 下面进行权限判别。要求：user是教务处，或者user是学生并且是本人。
        if authority.has_auth(auth_number, authority.AuthorityName.Office) \
                or authority.has_auth(auth_number, authority.AuthorityName.Root):
            validated_data['approved'] = 'approving'
            ins = super().create(validated_data)
            return ins
        elif authority.has_auth(auth_number, authority.AuthorityName.Student) \
                and getattr(profile, 'as_student') == student:
            validated_data['approved'] = 'approving'
            ins = super().create(validated_data)
            return ins
        else:
            raise serializers.ValidationError('Permission Denied.')

    class Meta:
        model = models.LeaveRecord
        fields = ('id', 'time_begin', 'time_end', 'note', 'student')


class LeaveApproveSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.LeaveRecord
        fields = ('id', 'approved')


class ClassroomRecordSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', queryset=models.AsStudent.objects.all())

    class Meta:
        model = models.ClassroomRecord
        fields = ('id', 'time_in', 'time_out', 'student', 'classroom_manage')


class ClassroomCheckSerializer(serializers.ModelSerializer):
    classroom_password = serializers.CharField(max_length=255, write_only=True)
    student_id = serializers.CharField(max_length=30, write_only=True)

    def create(self, validated_data):
        password = validated_data['classroom_password']
        sid = validated_data['student_id']
        classroom = models.ClassroomManage.objects.filter(password=password).first()
        student = models.AsStudent.objects.filter(username=sid).first()
        if classroom is None:
            raise serializers.ValidationError('Classroom password is wrong.')
        elif student is None:
            raise serializers.ValidationError('Student is not exists.')
        # 这里有比较复杂的逻辑内容。
        # 分别查询隶属该学生的【属于该教室的记录】和【不属于的记录】中time_out为null的记录。
        # 如果属于的记录非空，表示这是一次out记录，将其补全。同时不属于的记录全部修正。
        # 如果属于的记录为空。有两种情况。
        # 如果不属于的记录非空，表示这是一次非法操作，在补全不属于的记录的同时创建新记录。
        # 如果不属于的记录为空，那么直接创建新记录。
        all_records = models.ClassroomRecord.objects.filter(student=student).filter(time_out__isnull=True)  # 全部该学生的记录
        classroom_records = all_records.filter(classroom_manage=classroom).all()  # 获得所有同一个教室的记录
        other_classroom_records = all_records.filter(student=student).exclude(classroom_manage=classroom).all()  # 不同的记录
        (now_year, now_month, now_day, now_hour, now_minute, now_second, _, _, _) = time.localtime(time.time())
        time_str = '%04d-%02d-%02d %02d:%02d:%02d' % (now_year, now_month, now_day, now_hour, now_minute, now_second)
        for record in other_classroom_records:
            record.time_out = time_str
            record.save()
        if classroom_records:  # 属于该教室的记录非空
            for record in classroom_records:
                record.time_out = time_str
                record.save()
            ins = classroom_records[0]
            return ins
        else:
            data = {
                'time_in': time_str,
                'student': student,
                'classroom_manage': classroom
            }
            ins = super().create(data)
            return ins

    class Meta:
        model = models.ClassroomRecord
        fields = ('classroom_password', 'student_id')


class CourseScheduleSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all())
    classroom = serializers.PrimaryKeyRelatedField(queryset=models.Classroom.objects.all())

    class Meta:
        model = models.CourseSchedule
        fields = ('id', 'year', 'term', 'weeks', 'weekday', 'course_number', 'classroom', 'course')


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', queryset=models.AsStudent.objects.all())
    course_manage = serializers.PrimaryKeyRelatedField(queryset=models.CourseManage.objects.all())

    class Meta:
        model = models.AttendanceRecord
        fields = ('id', 'date', 'course_number', 'status', 'student', 'course_manage')


class SystemScheduleSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(queryset=models.SystemScheduleItem.objects.all(), many=True)

    class Meta:
        model = models.SystemSchedule
        fields = ('id', 'begin', 'end', 'items')


class SystemScheduleItemSerializer(serializers.ModelSerializer):
    system_schedule = serializers.PrimaryKeyRelatedField(queryset=models.SystemSchedule.objects.all())

    class Meta:
        model = models.SystemScheduleItem
        fields = ('id', 'begin', 'end', 'no', 'system_schedule')
