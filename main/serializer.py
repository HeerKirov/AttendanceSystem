from . import models
from rest_framework import serializers
from . import authority, utils, users
import time
from django.contrib.auth.models import User as defaultUser
from django.contrib.auth import authenticate

AuthorityChoice = [  # 用于User列表的可选权限列表
    ('Student', '学生权限'),
    ('Teacher', '教师权限'),
    ('Instructor', '辅导员权限'),
    ('Office', '教务处权限'),
]


class AuthoritySerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = models.Authority
        fields = ('id', 'auth')


class PasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=255, write_only=True)
    new_password = serializers.CharField(max_length=255, write_only=True)

    def update(self, instance, validated_data):
        user = authenticate(username=instance.username, password = validated_data['old_password'])
        if user is not None:
            user.set_password(validated_data['new_password'])
            user.save()
            return user
        else:
            raise serializers.ValidationError('Invalid check data.')

    class Meta:
        model = defaultUser
        fields = ('old_password', 'new_password')


class PasswordAdminSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(max_length=255, write_only=True)

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

    class Meta:
        model = defaultUser
        fields = ('new_password',)


class UserSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    username = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    authority = serializers.MultipleChoiceField(write_only=True, choices=AuthorityChoice)

    def create(self, validated_data):
        # 创建用户时，需要附加创建其关联模型。
        # 检查username查重。
        usernames = defaultUser.objects.filter(username=validated_data['username']).all()
        if len(usernames) > 0:
            raise serializers.ValidationError('Username is already exists!')
        # 需要检查创建的权限列表。
        for auth in validated_data['authority']:
            flag = False
            for item in AuthorityChoice:
                if auth == item[0]:
                    flag = True
                    break
            if not flag:
                raise serializers.ValidationError('You permitted a invalid authority.')

        return users.add_user(user_id=validated_data['username'],
                              name=validated_data['name'],
                              gender=validated_data['gender'],
                              password=validated_data['password'],
                              default_auth=validated_data['authority'])

    class Meta:
        model = models.User
        fields = ('id', 'username', 'password', 'name', 'gender', 'authority', 'register_time', 'last_login_time',)


class UserDetailSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = models.User
        fields = ('id', 'name', 'gender', 'register_time', 'last_login_time',)


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    username = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    name = serializers.CharField(max_length=16, write_only=True)
    gender = serializers.ChoiceField(choices=models.GENDER_ENUM, write_only=True, allow_null=True)
    classs = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    course_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)

    gender_related = serializers.SlugRelatedField(slug_field='gender', source='user', read_only=True)
    classs_name_related = serializers.SlugRelatedField(slug_field='name', source='classs', read_only=True)
    course_name_related = serializers.SlugRelatedField(slug_field='name', source='course_set', read_only=True, many=True)

    def create(self, validated_data):
        # 创建学生用户时，需要附加创建其关联模型。
        # 检查username查重。
        usernames = defaultUser.objects.filter(username=validated_data['username']).all()
        if len(usernames) > 0:
            raise serializers.ValidationError('Username is already exists!')
        profile = users.add_user(user_id=validated_data['username'],
                                 name=validated_data['name'],
                                 gender=validated_data['gender'],
                                 password=validated_data['password'],
                                 default_auth=['Student'])
        student = models.AsStudent.objects.filter(username=validated_data['username']).first()
        return student

    class Meta:
        model = models.AsStudent
        fields = ('id', 'username', 'password', 'name', 'gender', 'user', 'classs', 'course_set',
                  'gender_related', 'classs_name_related', 'course_name_related')


class StudentDetailSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    classs = serializers.PrimaryKeyRelatedField(read_only=True, allow_null=True)
    course_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)

    gender_related = serializers.SlugRelatedField(slug_field='gender', source='user', read_only=True)
    classs_name_related = serializers.SlugRelatedField(slug_field='name', source='classs', read_only=True)
    course_name_related = serializers.SlugRelatedField(slug_field='name', source='course_set', read_only=True,
                                                       many=True)

    class Meta:
        model = models.AsStudent
        fields = ('id', 'user', 'classs', 'course_set',
                  'gender_related', 'classs_name_related', 'course_name_related')


class TeacherSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)
    username = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    name = serializers.CharField(max_length=16, write_only=True)
    gender = serializers.ChoiceField(choices=models.GENDER_ENUM, write_only=True, allow_null=True)
    course_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    gender_related = serializers.SlugRelatedField(slug_field='gender', source='user', read_only=True)
    course_name_related = serializers.SlugRelatedField(slug_field='name', source='course_set', read_only=True,
                                                       many=True)

    def create(self, validated_data):
        # 创建学生用户时，需要附加创建其关联模型。
        # 检查username查重。
        usernames = defaultUser.objects.filter(username=validated_data['username']).all()
        if len(usernames) > 0:
            raise serializers.ValidationError('Username is already exists!')
        profile = users.add_user(user_id=validated_data['username'],
                                 name=validated_data['name'],
                                 gender=validated_data['gender'],
                                 password=validated_data['password'],
                                 default_auth=['Teacher'])
        teacher = models.AsTeacher.objects.filter(username=validated_data['username']).first()
        teacher.save()
        return teacher

    class Meta:
        model = models.AsTeacher
        fields = ('id', 'user', 'username', 'password', 'name', 'gender', 'course_set',
                  'gender_related', 'course_name_related')


class TeacherDetailSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)
    course_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    gender_related = serializers.SlugRelatedField(slug_field='gender', source='user', read_only=True)
    course_name_related = serializers.SlugRelatedField(slug_field='name', source='course_set', read_only=True,
                                                       many=True)

    class Meta:
        model = models.AsTeacher
        fields = ('id', 'user', 'course_set',
                  'gender_related', 'course_name_related')


class InstructorSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    username = serializers.CharField(max_length=30, write_only=True)
    password = serializers.CharField(max_length=255, write_only=True)
    name = serializers.CharField(max_length=16, write_only=True)
    gender = serializers.ChoiceField(choices=models.GENDER_ENUM, write_only=True, allow_null=True)
    classs_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)

    gender_related = serializers.SlugRelatedField(slug_field='gender', source='user', read_only=True)
    classs_name_related = serializers.SlugRelatedField(slug_field='name', source='classs_set', read_only=True,
                                                       many=True)

    def create(self, validated_data):
        # 创建学生用户时，需要附加创建其关联模型。
        # 检查username查重。
        usernames = defaultUser.objects.filter(username=validated_data['username']).all()
        if len(usernames) > 0:
            raise serializers.ValidationError('Username is already exists!')
        profile = users.add_user(user_id=validated_data['username'],
                                 name=validated_data['name'],
                                 gender=validated_data['gender'],
                                 password=validated_data['password'],
                                 default_auth=['Instructor'])
        instructor = models.AsInstructor.objects.filter(username=validated_data['username']).first()
        instructor.save()
        return instructor

    class Meta:
        model = models.AsInstructor
        fields = ('id', 'user', 'username', 'password', 'name', 'gender',  'classs_set',
                  'gender_related', 'classs_name_related')


class InstructorDetailSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(slug_field='username', read_only=True)
    classs_set = serializers.PrimaryKeyRelatedField(read_only=True, many=True)
    user = serializers.SlugRelatedField(slug_field='name', read_only=True)

    gender_related = serializers.SlugRelatedField(slug_field='gender', source='user', read_only=True)
    classs_name_related = serializers.SlugRelatedField(slug_field='name', source='classs_set', read_only=True,
                                                       many=True)

    class Meta:
        model = models.AsInstructor
        fields = ('id', 'user', 'classs_set',
                  'gender_related', 'classs_name_related')
        read_only_fields = ('username',)


class ClasssSerializer(serializers.ModelSerializer):
    as_student_set = serializers.SlugRelatedField(
        slug_field='username', queryset=models.AsStudent.objects.all(), many=True)
    as_instructor_set = serializers.SlugRelatedField(
        slug_field='username', queryset=models.AsInstructor.objects.all(), many=True)

    instructor_name_related = serializers.SlugRelatedField(slug_field='name', source='as_instructor_set',
                                                           read_only=True, many=True)
    student_name_related = serializers.SlugRelatedField(slug_field='name', source='as_student_set',
                                                        read_only=True, many=True)

    class Meta:
        model = models.Classs
        fields = ('id', 'grade', 'college', 'major', 'number', 'as_instructor_set', 'as_student_set',
                  'instructor_name_related', 'student_name_related')


class CourseBasicSerializer(serializers.ModelSerializer):
    teacher = serializers.SlugRelatedField(slug_field='username', queryset=models.AsTeacher.objects.all())
    as_student_set = serializers.SlugRelatedField(
        slug_field='username', queryset=models.AsStudent.objects.all(), many=True)
    course_schedule_set = serializers.PrimaryKeyRelatedField(
        queryset=models.CourseSchedule.objects.all(), many=True)
    exchange_record_set = serializers.PrimaryKeyRelatedField(
        read_only=True, many=True)

    student_name_related = serializers.SlugRelatedField(slug_field='name', source='as_student_set',
                                                        read_only=True, many=True)

    def create(self, validated_data):
        # 需要在创建对象时同时创建管理信息。
        ins = super().create(validated_data)
        manage = models.CourseManage(id=ins)
        manage.save()
        return ins

    class Meta:
        model = models.Course
        fields = ('id', 'name', 'teacher', 'as_student_set', 'course_schedule_set', 'exchange_record_set',
                  'student_name_related')


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


class ClassroomBasicDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Classroom
        fields = ('id', 'name', 'size')


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

    def update(self, instance, validated_data):
        if validated_data['approved'] == 'approving':
            raise serializers.ValidationError('You can not make it be approving.')
        if getattr(instance, 'approved') == 'pass':
            raise serializers.ValidationError('It is already passed.You can not change it.')
        return super().update(instance, validated_data)

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

        # 下面进行权限判别。要求：user是教务处/ROOT，或者user是学生并且是本人。
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

    def update(self, instance, validated_data):
        # 需要封锁对教师的权限。要求审批者只能是教务处/辅导员/ROOT。
        user = self.context['request'].user
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError('Unauthorized.')
        profile = user.profile  # 使用者的profile
        auth_number = getattr(profile, 'authority').auth  # 获得使用者账户的权限数字
        if authority.has_auth(auth_number, authority.AuthorityName.Teacher) \
                or authority.has_auth(auth_number, authority.AuthorityName.Office) \
                or authority.has_auth(auth_number, authority.AuthorityName.Root):
            if validated_data['approved'] == 'approving':
                raise serializers.ValidationError('You can not make it be approving.')
            if getattr(instance, 'approved') == 'pass':
                raise serializers.ValidationError('It is already passed.You can not change it.')
            return super().update(instance, validated_data)
        else:
            raise serializers.ValidationError('Permission Denied.')

    class Meta:
        model = models.LeaveRecord
        fields = ('id', 'approved')


class ClassroomRecordSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', queryset=models.AsStudent.objects.all())
    student_name_related = serializers.SlugRelatedField(slug_field='name', source='student', read_only=True)
    classroom_name_related = serializers.SlugRelatedField(slug_field='name', source='classroom_manage', read_only=True)

    class Meta:
        model = models.ClassroomRecord
        fields = ('id', 'time_in', 'time_out', 'student', 'classroom_manage',
                  'student_name_related', 'classroom_name_related')


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
    course_name_related = serializers.SlugRelatedField(slug_field='name', source='course', read_only=True)
    classroom_name_related = serializers.SlugRelatedField(slug_field='name', source='classroom', read_only=True)

    class Meta:
        model = models.CourseSchedule
        fields = ('id', 'year', 'term', 'weeks', 'weekday', 'course_number', 'classroom', 'course',
                  'course_name_related', 'classroom_name_related')


class AttendanceRecordSerializer(serializers.ModelSerializer):
    student = serializers.SlugRelatedField(slug_field='username', queryset=models.AsStudent.objects.all())
    course_manage = serializers.PrimaryKeyRelatedField(queryset=models.CourseManage.objects.all())

    class Meta:
        model = models.AttendanceRecord
        fields = ('id', 'date', 'course_number', 'status', 'student', 'course_manage')


class SystemScheduleSerializer(serializers.ModelSerializer):
    items = serializers.PrimaryKeyRelatedField(queryset=models.SystemScheduleItem.objects.all(), many=True)

    def validate(self, attrs):
        if attrs['begin'] > attrs['end']:
            raise serializers.ValidationError('begin time must be smaller than end time.')
        # 需要对时间的重叠进行验证。
        if self.instance is not None:
            schedules = models.SystemSchedule.objects.exclude(id=self.instance.id)
        else:
            schedules = models.SystemSchedule.objects.all()
        for schedule in schedules:
            if utils.check_crossing(attrs['begin'], attrs['end'], schedule.begin, schedule.end):
                raise serializers.ValidationError('Time part of system schedule must be unique.')
        return attrs

    class Meta:
        model = models.SystemSchedule
        fields = ('id', 'begin', 'end', 'items')


class SystemScheduleItemSerializer(serializers.ModelSerializer):
    system_schedule = serializers.PrimaryKeyRelatedField(queryset=models.SystemSchedule.objects.all())

    def validate(self, attrs):
        if attrs['begin'] > attrs['end']:
            raise serializers.ValidationError('begin time must be smaller than end time.')
        # 需要对时间表中每一块的时间重叠进行验证
        if self.instance is not None:
            items = models.SystemScheduleItem.objects.exclude(id=self.instance.id).\
                filter(system_schedule=self.instance.system_schedule)
        else:
            items = models.SystemScheduleItem.objects.filter(system_schedule=attrs['system_schedule'])
        for item in items:
            if utils.check_crossing(attrs['begin'], attrs['end'], item.begin, item.end):
                raise serializers.ValidationError('Time part of item in one system schedule must be unique.')
            elif attrs['no'] == item.no:
                raise serializers.ValidationError('Number of item must be unique.')
        return attrs

    class Meta:
        model = models.SystemScheduleItem
        fields = ('id', 'begin', 'end', 'no', 'system_schedule')
