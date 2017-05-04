import math
from . import models


AUTHORITY_BINARY = [  # 权限记录列表。(权限数字，英文标记，中文标记)
    (1, 'Root', '超级管理员权限'),
    (2, 'Student', '学生权限'),
    (4, 'Teacher', '教师权限'),
    (8, 'Instructor', '辅导员权限'),
    (16, 'Office', '教务处权限'),
    (32, 'Admin', '管理员权限'),
    (64, 'UserManager', '账户管理权限'),
    (128, 'StudentManager', '学生管理权限'),
    (256, 'TeacherManager', '教师管理权限'),
    (512, 'InstructorManager', '辅导员管理权限'),
    (1024, 'OfficeManager', '教务处管理权限'),
    (2048, 'CourseManager', '课程管理权限'),
    (4096, 'ClassroomManager', '教室管理权限'),
    (8192, 'ClassManager', '班级管理权限'),
    (16384, 'IsSelf', '本人或所有者使用权限'),
    (32768, 'IsParent', '上属者使用权限'),
    (65536, 'IsSub', '下属者使用权限')
]

BELONG_AUTHORITY = [  # 身份从属权限的名单
    'IsSelf',
    'IsParent',
    'Isub'
]


class AuthorityName:  # 普通权限的名称列表
    Root = 'Root'
    Student = 'Student'
    Teacher = 'Teacher'
    Instructor = 'Instructor'
    Office = 'Office'
    Admin = 'Admin'
    UserManager = 'UserManager'
    StudentManager = 'StudentManager'
    TeacherManager = 'TeacherManager'
    InstructorManager = 'InstructorManager'
    OfficeManager = 'OfficeManager'
    CourseManager = 'CourseManager'
    ClassroomManager = 'ClassroomManager'
    ClassManager = 'ClassManager'


class BelongName:  # 身份从属权限的名称列表
    IsSelf = 'IsSelf'
    IsParent = 'IsParent'
    IsSub = 'IsSub'

authority_list = {}  # "ENG":(CHINESE,BIN,N)


def update_authority():
    authority_list.clear()
    for n, en, chinese in AUTHORITY_BINARY:
        authority_list[en] = (chinese, int(math.log2(n)), n)


def has_auth(authority, auth_name):
    """
    检测给定的权限数字中有没有指定的目标权限。
    :param authority: 权限数字。
    :param auth_name: 目标权限的英文代号。
    :return: 返回一个布尔值。
    """
    binary = str(bin(authority))[2:]
    goal = authority_list[auth_name][1]
    # print("binary=%s,goal=%s,authname=%s" % (binary, goal, auth_name))
    return goal is not None and len(binary) > goal and binary[-goal-1] == '1'


def add_auth(authority, args):
    """
    向权限数字中添加权限。
    :param authority: 权限数字
    :param args: 权限列表
    :return: 返回新的权限数字，或者当出错时返回None.
    """
    # todo 实验性写法，为了保证安全必须使用二进制重写。
    for name in args:
        if authority_list[name] is not None:
            authority += authority_list[name][2]
        else:
            return None
    return authority


def belong_to(obj, goal):
    """
    进行泛判断，goal是否是obj的上属、拥有者或者是其本身。
    :param obj: 要判断的下属目标
    :param goal: 要判断的上属目标
    :return: 返回一个布尔值
    """
    if type(obj) == type(goal) and obj == goal:
        return True
    goal_auth = goal.authority.auth  # 预先获得目标的权限数字，以备使用
    goal_is_office = has_auth(goal_auth, AuthorityName.Office)
    # goal_is_admin = has_auth(goal_auth, AuthorityName.Admin)

    if isinstance(obj, models.User):  # 源是用户，那么获取权限判断可能的上属。
        auth_number = obj.authority.auth
        if has_auth(auth_number, AuthorityName.Student):  # 判断用户身份
            if goal_is_office:
                return True
            student_class = obj.as_student.classs
            student_course_set = obj.as_student.course_set
            if belong_to(student_class, goal):
                return True
            for student_course in student_course_set.all():
                if belong_to(student_course, goal):
                    return True
        if has_auth(auth_number, AuthorityName.Teacher):
            if goal_is_office:
                return True
        if has_auth(auth_number, AuthorityName.Instructor):
            if goal_is_office:
                return True
        if has_auth(auth_number, AuthorityName.Office) or has_auth(auth_number, AuthorityName.Admin):
            if obj.id == goal.id:
                return True
    elif isinstance(obj, models.Classs):  # 源是一个班级。
        if goal_is_office:
            return True
        class_instructor = [ins.user for ins in obj.as_instructor_set.all()]
        for user in class_instructor:
            if belong_to(user, goal):
                return True
    elif isinstance(obj, models.Course):  # 源是一门课程
        if goal_is_office:
            return True
        course_teacher = [tea.user for tea in obj.teacher.all()]
        for user in course_teacher:
            if belong_to(user, goal):
                return False
    elif isinstance(obj, models.CourseManage):  # 源是课程管理信息。
        return belong_to(obj.id, goal)
    elif isinstance(obj, models.Classroom):  # 源是教室。
        return False  # 教室不参与这个从属级别图。
    elif isinstance(obj, models.ClassroomManage):
        return False
    elif isinstance(obj, models.AttendanceRecord):  # 出勤记录
        return belong_to(obj.student, goal)
    elif isinstance(obj, models.LeaveRecord):  # 请假记录
        return belong_to(obj.student, goal)
    elif isinstance(obj, models.ClassroomRecord):  # 教室使用记录
        return belong_to(obj.student, goal)
    elif isinstance(obj, models.ExchangeRecord):  # 调课记录
        return belong_to(obj.course, goal)
    elif isinstance(obj, models.CourseSchedule):  # 上课时间安排
        return belong_to(obj.course, goal)
    return False


def belong_to_side(obj, goal):
    """
    狭义的从属关系判断，仅在obj是goal或者obj是goal的附属时返回真。
    :param obj: 判断源
    :param goal: 判断目标
    :return: 返回一个布尔值。
    """
    if type(obj) == type(goal) and obj == goal:
        return True
    goal_auth = goal.authority.auth  # 预先获得目标的权限数字，以备使用
    goal_is_office = has_auth(goal_auth, AuthorityName.Office)

    if isinstance(obj, models.AttendanceRecord):  # 出勤记录
        return belong_to_side(obj.student, goal)
    elif isinstance(obj, models.LeaveRecord):  # 请假记录
        return belong_to_side(obj.student, goal)
    elif isinstance(obj, models.ClassroomRecord):  # 教室使用记录
        return belong_to_side(obj.student, goal)
    elif isinstance(obj, models.ExchangeRecord):  # 调课记录
        return belong_to_side(obj.course, goal)
    elif isinstance(obj, models.CourseSchedule):  # 上课时间安排
        return belong_to_side(obj.course, goal)
    else:
        return False

update_authority()
