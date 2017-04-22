from django.db import models

GENDER_ENUM = (
    ('MALE', 'MALE'),
    ('FEMALE', 'FEMALE')
)
ATTENDANCE_STATUS = (

)
APPROVE_STATUS = (
    ('approving', '审批中'),
    ('reject', '被拒绝'),
    ('pass', '通过')
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
# Create your models here.


# 使用者用户模型
class User(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=16)
    gender = models.CharField(max_length=6, choices=GENDER_ENUM)
    password = models.CharField(max_length=255)
    register_time = models.DateTimeField()
    last_login_time = models.DateTimeField()
    is_active = models.BooleanField()
    # asStudent, asTeacher, asInstructor, asOffice, asAdmin, Authority


# 使用者权限
class Authority(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # todo 需要思考一种补充动态权限的方式


# 作为辅导员
class AsInstructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # classs_set


# 班级(注意这里写了3个s！！！！)
class Classs(models.Model):
    grade = models.IntegerField()
    college = models.CharField(max_length=16, blank=True)
    major = models.CharField(max_length=25, blank=True)
    no = models.IntegerField()
    as_instructor_set = models.ManyToManyField(AsInstructor, related_name='classs_set')
    # as_student_set


# 作为教师
class AsTeacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # course_set


# 作为教务处
class AsOffice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


# 作为管理员
class AsAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


# 课程
class Course(models.Model):
    name = models.CharField(max_length=50)
    teacher = models.ForeignKey(AsTeacher, related_name='course_set', on_delete=models.SET_NULL, null=True)
    # as_student_set
    # course_schedule_set
    # exchange_set
    # attendance_set


# 作为学生
class AsStudent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    classs = models.ForeignKey(Classs, related_name='as_student_set', on_delete=models.SET_NULL, null=True)
    course_set = models.ManyToManyField(Course, related_name='as_student_set')
    # classroom_record_set
    # leave_record_set
    # attendance_record_set


# 教室
class Classroom(models.Model):
    name = models.CharField(max_length=16, unique=True)
    size = models.IntegerField()
    # course_schedule_set
    # classroom_record_set


# 上课时间安排
class CourseSchedule(models.Model):
    year = models.IntegerField()
    term = models.IntegerField()
    weeks = models.CharField(max_length=255)
    weekday = models.CharField(max_length=255)
    course_number = models.CharField(max_length=255)
    classroom = models.ForeignKey(Classroom, related_name='course_schedule_set', on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, related_name='course_schedule_set', on_delete=models.CASCADE)


# 学生出勤记录
class AttendanceRecord(models.Model):
    year = models.IntegerField()
    term = models.IntegerField()
    weeks = models.IntegerField()
    weekday = models.IntegerField()
    course_number = models.CharField(max_length=255)
    status = models.CharField(choices=ATTENDANCE_STATUS, max_length=12)
    student = models.ForeignKey(AsStudent, related_name='attendance_record_set', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='attendance_record_set', on_delete=models.CASCADE)


# 学生请假记录
class LeaveRecord(models.Model):
    time_begin = models.DateTimeField()
    time_end = models.DateTimeField()
    note = models.TextField(max_length=200, null=True, blank=True)
    approved = models.CharField(max_length=10, choices=APPROVE_STATUS)
    student = models.ForeignKey(AsStudent, related_name='leave_record_set', on_delete=models.CASCADE)


# 教室使用记录
class ClassroomRecord(models.Model):
    time_in = models.DateTimeField()
    time_out = models.DateTimeField(null=True, blank=True)
    student = models.ForeignKey(AsStudent, related_name='classroom_record_set', on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, related_name='classroom_record_set', on_delete=models.CASCADE)


# 调课记录
class ExchangeRecord(models.Model):
    year = models.IntegerField()
    term = models.IntegerField()
    from_week = models.CharField(max_length=255)
    from_weekday = models.CharField(max_length=255)
    from_course_number = models.CharField(max_length=255)
    goal_week = models.CharField(max_length=255)
    goal_weekday = models.CharField(max_length=255)
    goal_course_number = models.CharField(max_length=255)
    note = models.TextField(max_length=200, null=True, blank=True)
    approved = models.CharField(choices=APPROVE_STATUS, max_length=10)
    course = models.ForeignKey(Course, related_name='exchange_record_set', on_delete=models.CASCADE)


# 系统时间表
class SystemSchedule(models.Model):
    begin = models.DateField()
    end = models.DateField()
    course_number = models.IntegerField()


# 系统时间表子表-课时时间
class SystemScheduleItem(models.Model):
    begin = models.TimeField()
    end = models.TimeField()
    no = models.IntegerField()
    system_schedule = models.ForeignKey(SystemSchedule, related_name='item', on_delete=models.CASCADE)
