from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import User as defaultUser

GENDER_ENUM = (
    ('MALE', '男'),
    ('FEMALE', '女')
)
ATTENDANCE_STATUS = (
    ('NONE', '未到'),
    ('LATE', '迟到'),
    ('LEAVE', '早退'),
    ('ABSENT', '缺勤'),
    ('NORMAL', '正常')
)
WEEKDAYS = (
    ('Monday', '周一'),
    ('Tuesday', '周二'),
    ('Wednesday', '周三'),
    ('Thursday', '周四'),
    ('Friday', '周五'),
    ('Saturday', '周六'),
    ('Sunday', '周日')
)

AuthUser = get_user_model()
# Create your models here.


# 使用者用户模型
class User(models.Model):
    id = models.OneToOneField(defaultUser, related_name='profile', primary_key=True, on_delete=models.CASCADE)
    username = models.CharField(unique=True, max_length=30)
    name = models.CharField(max_length=16, null=True, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_ENUM, null=True, blank=True)
    register_time = models.DateTimeField(auto_now_add=True)
    last_login_time = models.DateTimeField(default='1970-01-01')
    # asStudent, asTeacher, asInstructor, asOffice, asAdmin, Authority

    def __str__(self):
        return "<%s - %s>" % (self.username, self.name)


# 使用者权限
class Authority(models.Model):
    id = models.OneToOneField(defaultUser, on_delete=models.CASCADE, related_name='authority', primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='authority')
    auth = models.BigIntegerField()

    def __str__(self):
        return "%s" % (self.user,)


# 作为学生
class AsStudent(models.Model):
    id = models.OneToOneField(defaultUser, on_delete=models.CASCADE, related_name='as_student', primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='as_student')
    username = models.CharField(max_length=30, unique=True)
    classs = models.ForeignKey('Classs', related_name='as_student_set', on_delete=models.SET_NULL, null=True)
    course_set = models.ManyToManyField('Course', related_name='as_student_set')

    def get_name(self):
        return self.user.name

    name = property(get_name)

    def __str__(self):
        return "%s" % (self.user,)
    # classroom_record_set
    # leave_record_set
    # attendance_record_set


# 作为教师
class AsTeacher(models.Model):
    id = models.OneToOneField(defaultUser, on_delete=models.CASCADE, related_name='as_teacher', primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='as_teacher')
    username = models.CharField(max_length=30, unique=True)

    def get_name(self):
        return self.user.name

    name = property(get_name)

    def __str__(self):
        return "%s" % (self.user,)
    # course_set


# 作为辅导员
class AsInstructor(models.Model):
    id = models.OneToOneField(defaultUser, on_delete=models.CASCADE, related_name='as_instructor', primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='as_instructor')
    username = models.CharField(max_length=30, unique=True)

    def get_name(self):
        return self.user.name

    name = property(get_name)

    def __str__(self):
        return "%s" % (self.user,)
    # classs_set


# 班级(注意这里写了3个s！！！！)
class Classs(models.Model):
    id = models.CharField(max_length=16, primary_key=True, unique=True)
    grade = models.IntegerField()
    college = models.CharField(max_length=16, blank=True)
    major = models.CharField(max_length=25, blank=True)
    number = models.IntegerField()
    as_instructor_set = models.ManyToManyField(AsInstructor, related_name='classs_set')
    # as_student_set

    def get_name(self):
        return "%s%s-%s" % (self.major, self.grade, self.number)

    name = property(get_name)

    def __str__(self):
        return "<%s-%s-%s.%s>" % (self.college, self.major, self.grade, self.number)


# 课程
class Course(models.Model):
    id = models.CharField(max_length=16, primary_key=True, unique=True)
    name = models.CharField(max_length=50)
    year = models.IntegerField(default=1970)
    term = models.IntegerField(default=1)
    teacher = models.ForeignKey(AsTeacher, related_name='course_set', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return "<%s - %s by %s>" % (self.id, self.name, self.teacher)
    # as_student_set
    # course_schedule_set


class CourseManage(models.Model):
    id = models.OneToOneField(Course, related_name='course_manage', primary_key=True, on_delete=models.CASCADE)
    # attendance_record_set

    def __str__(self):
        return self.id


# 教室
class Classroom(models.Model):
    id = models.CharField(max_length=16, primary_key=True, unique=True)
    name = models.CharField(max_length=16, unique=True)
    size = models.IntegerField()

    def __str__(self):
        return "<%s - %s>" % (self.id, self.name)
    # course_schedule_set


class ClassroomManage(models.Model):
    id = models.OneToOneField(Classroom, related_name='classroom_manage', primary_key=True, on_delete=models.CASCADE)
    password = models.CharField(max_length=255, null=True, blank=True, unique=True)

    def get_name(self):
        return self.id.name

    name = property(get_name)

    def __str__(self):
        return "%s" % (self.id,)
    # classroom_record_set


# 上课时间安排
class CourseSchedule(models.Model):
    weeks = models.CharField(max_length=255)  # 周数
    weekday = models.CharField(max_length=255)  # 星期几
    course_number = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom, related_name='course_schedule_set', on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, related_name='course_schedule_set', on_delete=models.CASCADE)

    def __str__(self):
        return "<Week[%s]-[%s] Course[%s] of %s in %s>" % \
               (self.weeks, self.weekday, self.course_number, self.course, self.classroom)


# 学生出勤记录
class AttendanceRecord(models.Model):
    date = models.DateField(default='1970-01-01')
    course_number = models.IntegerField()
    status = models.CharField(choices=ATTENDANCE_STATUS, max_length=12)
    student = models.ForeignKey(AsStudent, related_name='attendance_record_set', on_delete=models.CASCADE)
    course_manage = models.ForeignKey(CourseManage, related_name='attendance_record_set', on_delete=models.CASCADE)

    def __str__(self):
        return "<Attendance %s in %s : %s>" % (self.course_number, self.date, self.status)


# 教室使用记录
class ClassroomRecord(models.Model):
    time_in = models.DateTimeField()
    time_out = models.DateTimeField(null=True, blank=True)
    student = models.ForeignKey(AsStudent, related_name='classroom_record_set', on_delete=models.CASCADE)
    classroom_manage = models.ForeignKey(ClassroomManage, related_name='classroom_record_set', on_delete=models.CASCADE)

    def __str__(self):
        return "<CR %s to %s of %s>" % (self.time_in, self.time_out, self.classroom_manage)


# 系统时间表
class SystemSchedule(models.Model):
    begin = models.DateField()
    end = models.DateField()
    year = models.IntegerField(default=1970)
    term = models.IntegerField(default=1)
    # course_number = models.IntegerField()  # 每天的课程数量
    # item

    def __str__(self):
        return "<System Schedule %s to %s>" % (self.begin, self.end)


# 系统时间表子表-课时时间
class SystemScheduleItem(models.Model):
    begin = models.TimeField()
    end = models.TimeField()
    no = models.IntegerField()
    system_schedule = models.ForeignKey(SystemSchedule, related_name='items', on_delete=models.CASCADE)

    def __str__(self):
        return "<Item No.%s %s to %s>" % (self.no, self.begin, self.end)
