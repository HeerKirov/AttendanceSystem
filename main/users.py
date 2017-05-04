from django.contrib.auth.models import User as defaultUser
from . import models
from .authority import authority_list, AuthorityName


def add_user(user_id, name, gender, password, default_auth=None):
    """
    按照程序规范创建一个用户.
    :param user_id: 用户的ID。不能更改。
    :param name: 用户姓名。
    :param gender: 性别，请使用MALE或FEMALE
    :param password: 密码。
    :param default_auth: 默认的权限列表，该列表内的权限也会被认可为职位
    :return: 返回新的User对象(非defaultUser).
    """
    user_model = defaultUser.objects.create_user(user_id, password=password)
    user = models.User(id=user_model, username=user_id, name=name, gender=gender)
    # 计算一下权限数字，并执行一些相关操作
    auth_number = 0
    if default_auth is not None:
        for auth in default_auth:
            auth_number += authority_list[auth][2]  # 根据定义，这个项是十进制数字
            if auth == AuthorityName.Student:
                set_student(user)
            if auth == AuthorityName.Teacher:
                set_teacher(user)
            if auth == AuthorityName.Instructor:
                set_instructor(user)

    user_auth = models.Authority(
        id=user_model,
        user=user,
        auth=auth_number
    )
    user.save()
    user_auth.save()


def set_student(user, value=True):
    """
    将目标用户设置为学生账户/取消。这个函数只负责操作背后的关联部分，不负责修改权限。
    :param user: 目标账户的User模型。
    :return: 返回该用户的AsStudent模型或返回None。
    """
    if value:
        if hasattr(user, 'as_student'):
            return user.as_student
        else:
            student = models.AsStudent(
                id=user.id,
                user=user,
                username=user.username
            )
            student.save()
            return student
    else:
        if hasattr(user, 'as_student'):
            student = user.as_student
            student.delete()
            return None
        else:
            return None


def set_teacher(user, value=True):
    """
    将目标用户设置为教师账户/取消。这个函数只负责操作背后的关联部分，不负责修改权限。
    :param user: 目标账户的User模型。
    :return: 返回该用户的AsTeacher模型或返回None。
    """
    if value:
        if hasattr(user, 'as_teacher'):
            return user.as_teacher
        else:
            teacher = models.AsTeacher(
                id=user.id,
                user=user,
                username=user.username
            )
            teacher.save()
            return teacher
    else:
        if hasattr(user, 'as_teacher'):
            teacher = user.as_teacher
            teacher.delete()
            return None
        else:
            return None


def set_instructor(user, value=True):
    """
    将目标用户设置为辅导员账户/取消。这个函数只负责操作背后的关联部分，不负责修改权限。
    :param user: 目标账户的User模型。
    :return: 返回该用户的AsInstructor模型或返回None。
    """
    if value:
        if hasattr(user, 'as_instructor'):
            return user.as_instructor
        else:
            instructor = models.AsInstructor(
                id=user.id,
                user=user,
                username=user.username
            )
            instructor.save()
            return instructor
    else:
        if hasattr(user, 'as_instructor'):
            instructor = user.as_instructor
            instructor.delete()
            return None
        else:
            return None


