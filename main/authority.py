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
    (1024, 'CourseManager', '课程管理权限'),
    (2048, 'ClassroomManager', '教室管理权限'),
    (4096, 'ClassManager', '班级管理权限'),
    (8192, 'IsSelf', '本人或所有者使用权限'),
    (16384, 'IsParent', '上属者使用权限'),
    (32768, 'IsSub', '下属者使用权限')
]

BELONG_AUTHORITY = [  # 身份从属权限的名单
    'IsSelf',
    'IsParent',
    'IsSub'
]

ALL_AUTHORITY = [  # 全权限名单
    'All',
]


class AllAuthorityName:  # 全权限代表名称
    All = 'All'


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


def all_auth(authority):
    """
    将权限数字转化为完整的英文权限代号列表。
    :param authority: 权限数字。
    :return: 返回一个列表。
    """
    ret = []
    for en, (_, _, _) in authority_list.items():
        if has_auth(authority, en):
            ret.append(en)
    return ret


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


def get_profile(user):
    """
    获取目标model的Profile模型。
    :param user: 目标model
    :return: 
    """
    if isinstance(user, models.defaultUser):
        return getattr(user, 'profile')
    if isinstance(user, models.AsStudent):
        return user.user
    elif isinstance(user, models.AsTeacher):
        return user.user
    elif isinstance(user, models.AsInstructor):
        return user.user
    elif isinstance(user, models.Authority):
        return user.user
    elif isinstance(user, models.CourseManage):
        return user.id
    elif isinstance(user, models.ClassroomManage):
        return user.id
    elif isinstance(user, models.CourseSchedule):
        return user.course
    elif isinstance(user, models.AttendanceRecord):
        return user.student
    elif isinstance(user, models.ClassroomRecord):
        return user.classroom_manage.id
    else:
        return user


def belong_to(obj, goal):
    """
    进行泛判断，goal是否是obj的上属、拥有者或者是其本身。
    :param obj: 要判断的下属目标
    :param goal: 要判断的上属目标
    :return: 返回一个布尔值
    """
    obj = get_profile(obj)
    goal = get_profile(goal)
    if type(obj) == type(goal) and obj == goal:
        return True
    goal_auth = 0
    if hasattr(goal, 'authority'):
        goal_auth = goal.authority.auth  # 预先获得目标的权限数字，以备使用
    goal_is_office = has_auth(goal_auth, AuthorityName.Office)
    goal_is_root = has_auth(goal_auth, AuthorityName.Root)
    if goal_is_root:
        return True

    if isinstance(obj, models.User):  # 源是用户，那么获取权限判断可能的上属。
        auth_number = obj.authority.auth
        if has_auth(auth_number, AuthorityName.Student):  # 判断用户身份,这是学生身份
            # 学生身份可能的直接上属来源有：class，course，教务处，学生管理权限。
            if goal_is_office:  # 首先直接判断目标是否是教务处
                return True
            if has_auth(goal_auth, AuthorityName.StudentManager):  # 然后，如果目标拥有学生管理权限
                return True
            if hasattr(obj.as_student, 'classs'):  # 保证不会报错
                student_class = obj.as_student.classs
                if belong_to(student_class, goal):  # 这里是判断是上属班级是不是目标的下属。
                    return True
            if hasattr(obj.as_student, 'course_set'):  # 保证不会出错
                student_course_set = obj.as_student.course_set
                for student_course in student_course_set.all():
                    if belong_to(student_course, goal):
                        return True
        if has_auth(auth_number, AuthorityName.Teacher):
            if goal_is_office:
                return True
            if has_auth(goal_auth, AuthorityName.TeacherManager):  # 然后，检测目标是不是拥有教师管理权限
                return True
        if has_auth(auth_number, AuthorityName.Instructor):
            if goal_is_office:
                return True
            if has_auth(goal_auth, AuthorityName.InstructorManager):  # 然后，检测目标是不是拥有辅导员管理权限
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
        course_teacher = obj.teacher  # 已修正bug：需要注意的是，在现有模型中课程只有一位教师。
        if belong_to(course_teacher, goal):
            return False
    # elif isinstance(obj, models.CourseManage):  # 源是课程管理信息。
    #     return belong_to(obj.id, goal)
    elif isinstance(obj, models.Classroom):  # 源是教室。
        return False  # 教室不参与这个从属级别图。
    # elif isinstance(obj, models.ClassroomManage):
    #     return False
    # elif isinstance(obj, models.AttendanceRecord):  # 出勤记录
    #     return belong_to(obj.student, goal)
    # elif isinstance(obj, models.LeaveRecord):  # 请假记录
    #     return belong_to(obj.student, goal)
    # elif isinstance(obj, models.ClassroomRecord):  # 教室使用记录
    #     return belong_to(obj.student, goal)
    # elif isinstance(obj, models.ExchangeRecord):  # 调课记录
    #     return belong_to(obj.course, goal)
    # elif isinstance(obj, models.CourseSchedule):  # 上课时间安排
    #     return belong_to(obj.course, goal)
    return False


def belong_to_side(obj, goal):
    """
    狭义的从属关系判断，仅在obj是goal或者obj是goal的附属时返回真。
    :param obj: 判断源
    :param goal: 判断目标
    :return: 返回一个布尔值。
    """
    obj = get_profile(obj)
    goal = get_profile(goal)
    if type(obj) == type(goal) and obj == goal:
        return True
    # goal_auth = goal.authority.auth  # 预先获得目标的权限数字，以备使用
    # goal_is_office = has_auth(goal_auth, AuthorityName.Office)
    return False
    # if isinstance(obj, models.AttendanceRecord):  # 出勤记录
    #     return belong_to_side(obj.student, goal)
    # elif isinstance(obj, models.LeaveRecord):  # 请假记录
    #     return belong_to_side(obj.student, goal)
    # elif isinstance(obj, models.ClassroomRecord):  # 教室使用记录
    #     return belong_to_side(obj.student, goal)
    # elif isinstance(obj, models.ExchangeRecord):  # 调课记录
    #     return belong_to_side(obj.course, goal)
    # elif isinstance(obj, models.CourseSchedule):  # 上课时间安排
    #     return belong_to_side(obj.course, goal)
    # else:
    #     return False

update_authority()
