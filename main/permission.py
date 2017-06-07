from rest_framework.permissions import BasePermission, SAFE_METHODS
from . import models
from . import authority as auth_check
from .authority import AuthorityName, BelongName, AllAuthorityName


class UserAuthorityPermission(BasePermission):
    auth_number = {}  # 请使用键值对表示目标请求以及权限。权限使用元组表示列表。

    def has_permission(self, request, view):
        # print('has_permission:%s' % (request.method,))
        user = request.user  # 获取用户User模型
        if not user.is_authenticated:
            return False
        authority = user.authority  # 获取权限模型
        if authority is None:
            return False
        number = authority.auth  # 获取权限数字
        for method, permissions in self.auth_number.items():  # 查找目标类型
            if permissions is not None and ((method == 'PUT' and request.method == 'PATCH') or request.method == method):
                for item in permissions:  # 遍历目标类型的许可,这里的item是目标权限字符串
                    # 这个for之内不允许返回False。
                    if item in auth_check.ALL_AUTHORITY:  # 全权限系列
                        return True
                    elif item in auth_check.BELONG_AUTHORITY:  # 如果目标权限是从属权限
                        return True
                    elif auth_check.has_auth(number, item):  # 不是就执行一般判断
                        return True
                return False
        return False

    def has_object_permission(self, request, view, obj):
        # print('has_obj_permission:%s' % (request.method, ))
        user = request.user  # 获取用户User模型
        if not user.is_authenticated:
            return False
        authority = user.authority  # 获取权限模型
        if authority is None:
            return False
        number = authority.auth  # 获取权限数字
        for method, permissions in self.auth_number.items():  # 查找目标类型
            if permissions is not None and ((method == 'PUT' and request.method == 'PATCH') or request.method == method):
                for item in permissions:  # 遍历目标类型的许可,这里的item是目标权限字符串
                    # 修复错误：在这个for循环之内不能returnFalse！否则会打破Or联结。
                    if item in auth_check.ALL_AUTHORITY:
                        return True
                    elif item in auth_check.BELONG_AUTHORITY:  # 如果目标权限是从属权限
                        if item == auth_check.BelongName.IsSelf:
                            if auth_check.belong_to_side(obj, user.profile):
                                return True
                        elif item == auth_check.BelongName.IsParent:
                            if auth_check.belong_to(obj, user):
                                return True
                        elif item == auth_check.BelongName.IsSub:
                            if auth_check.belong_to(user, obj):
                                return True
                    elif auth_check.has_auth(number, item):  # 不是就执行一般判断
                        return True
                return False
        return False


class Action:
    class AuthorityPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.Root,),
            'PUT': (AuthorityName.Root,),
        }

    class PasswordAdminPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.UserManager, AuthorityName.Root),
            'PUT': (AuthorityName.UserManager, AuthorityName.Root)
        }


class User:
    class UserPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.UserManager, AuthorityName.Root),
            'POST': (AuthorityName.UserManager, AuthorityName.Root)
        }

    class UserDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.UserManager, AuthorityName.Root),
            'PUT': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.UserManager, AuthorityName.Root),
            'DELETE': (AuthorityName.UserManager, AuthorityName.Root),
        }

    class StudentPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.StudentManager, AuthorityName.Root),
            'POST': (AuthorityName.StudentManager, AuthorityName.Root)
        }

    class StudentDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.StudentManager, AuthorityName.Root),
            'PUT': (AuthorityName.StudentManager, AuthorityName.Root),
            'DELETE': (AuthorityName.StudentManager, AuthorityName.Root)
        }

    class TeacherPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.TeacherManager, AuthorityName.Root),
            'POST': (AuthorityName.TeacherManager, AuthorityName.Root)
        }

    class TeacherDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.TeacherManager, AuthorityName.Root),
            'PUT': (AuthorityName.TeacherManager, AuthorityName.Root),
            'DELETE': (AuthorityName.TeacherManager, AuthorityName.Root)
        }

    class InstructorPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.InstructorManager, AuthorityName.Root),
            'POST': (AuthorityName.InstructorManager, AuthorityName.Root)
        }

    class InstructorDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.InstructorManager, AuthorityName.Root),
            'PUT': (AuthorityName.InstructorManager, AuthorityName.Root),
            'DELETE': (AuthorityName.InstructorManager, AuthorityName.Root)
        }


class Item:

    class ClasssPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.ClassManager, AuthorityName.Root),
            'POST': (AuthorityName.ClassManager, AuthorityName.Root)
        }

    class ClasssDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsParent, BelongName.IsSub, AuthorityName.ClassManager, AuthorityName.Root),
            'PUT': (AuthorityName.ClassManager, AuthorityName.Root),
            'DELETE': (AuthorityName.ClassManager, AuthorityName.Root)
        }

    class CourseBasicPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.CourseManager, AuthorityName.Root),
            'POST': (AuthorityName.CourseManager, AuthorityName.Root)
        }

    class CourseBasicDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSub, BelongName.IsParent, AuthorityName.CourseManager, AuthorityName.Root),
            'PUT': (AuthorityName.CourseManager, AuthorityName.Root),
            'DELETE': (AuthorityName.CourseManager, AuthorityName.Root)
        }

    class CourseManagePermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.CourseManager, AuthorityName.Root)
        }

    class CourseManageDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsParent, AuthorityName.CourseManager, AuthorityName.Root)
        }

    class ClassroomPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AllAuthorityName.All, AuthorityName.Root),
            'POST': (AuthorityName.ClassroomManager, AuthorityName.Root),
            'PUT': (AuthorityName.ClassroomManager, AuthorityName.Root),
            'DELETE': (AuthorityName.ClassroomManager, AuthorityName.Root)
        }

    class ClassroomManagePermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.ClassroomManager, AuthorityName.Root),
            'PUT': (AuthorityName.ClassroomManager, AuthorityName.Root),
        }


class Record:
    class ExchangeRecordPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.CourseManager, AuthorityName.Office, AuthorityName.Root)
        }

    class ExchangeDetailRecordPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsParent, BelongName.IsSub, BelongName.IsSelf,
                    AuthorityName.CourseManager, AuthorityName.Office, AuthorityName.Root)
        }

    class ExchangeApplyPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.CourseManager, AuthorityName.Office, AuthorityName.Root),
            'POST': (AllAuthorityName.All, AuthorityName.Root)
        }

    class ExchangeApprovePermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.CourseManager, AuthorityName.Office, AuthorityName.Root),
            'PUT': (AuthorityName.CourseManager, AuthorityName.Office, AuthorityName.Root)
        }

    class LeaveRecordPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.Office, AuthorityName.StudentManager, AuthorityName.Root)
        }

    class LeaveDetailRecordPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent,
                    AuthorityName.Office, AuthorityName.StudentManager, AuthorityName.Root)
        }

    class LeaveApplyPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.Office, AuthorityName.StudentManager, AuthorityName.Root),
            'POST': (AllAuthorityName.All, AuthorityName.Root)
        }

    class LeaveApprovePermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsParent, AuthorityName.Office, AuthorityName.Root),
            'PUT': (BelongName.IsParent, AuthorityName.Office, AuthorityName.Root)
        }

    class ClassroomRecordPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.ClassroomManager, AuthorityName.Root)
        }

    class ClassroomRecordDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsParent, BelongName.IsSelf, AuthorityName.ClassroomManager, AuthorityName.Root)
        }

    class CourseSchedulePermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.CourseManager, AuthorityName.Root),
            'POST': (AuthorityName.CourseManager, AuthorityName.Root)
        }

    class CourseScheduleDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsParent, BelongName.IsSub, BelongName.IsSelf,
                    AuthorityName.CourseManager, AuthorityName.Root),
            'PUT': (AuthorityName.CourseManager, AuthorityName.Root),
            'DELETE': (AuthorityName.CourseManager, AuthorityName.Root)
        }

    class AttendanceRecordPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.Office, AuthorityName.StudentManager, AuthorityName.Root)
        }

    class AttendanceRecordDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent,
                    AuthorityName.Office, AuthorityName.StudentManager, AuthorityName.Root)
        }


class Schedule:
    class SystemSchedulePermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.Admin, AuthorityName.Root),
            'POST': (AuthorityName.Admin, AuthorityName.Root),
            'PUT': (AuthorityName.Admin, AuthorityName.Root),
            'DELETE': (AuthorityName.Admin, AuthorityName.Root)
        }

    class SystemScheduleItemPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.Admin, AuthorityName.Root),
            'POST': (AuthorityName.Admin, AuthorityName.Root)
        }




