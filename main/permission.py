from rest_framework.permissions import BasePermission, SAFE_METHODS
from . import models
from . import authority as auth_check
from .authority import AuthorityName, BelongName


class IsSelf(BasePermission):  # user的查看目标是user本身
    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated() and user.username == obj.username


class IsParent(BasePermission):  # 是查看目标的上属
    def has_object_permission(self, request, view, obj):
        user = request.user
        return auth_check.belong_to(obj, user)


class IsSub(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return auth_check.belong_to(user, obj)


class UserAuthorityPermission(BasePermission):
    auth_number = {}  # 请使用键值对表示目标请求以及权限。权限使用元组表示列表。

    def has_permission(self, request, view):
        print('has_permission:%s' % (request.method,))
        user = request.user  # 获取用户User模型
        if not user.is_authenticated:
            return False
        authority = user.authority  # 获取权限模型
        if authority is None:
            return False
        number = authority.auth  # 获取权限数字
        for method, permissions in self.auth_number.items():  # 查找目标类型
            if permissions is not None and request.method == method:
                for item in permissions:  # 遍历目标类型的许可,这里的item是目标权限字符串
                    # 这个for之内不允许返回False。
                    if item in auth_check.BELONG_AUTHORITY:  # 如果目标权限是从属权限
                        return True
                    elif auth_check.has_auth(number, item):  # 不是就执行一般判断
                        return True
                return False
        return False

    def has_object_permission(self, request, view, obj):
        print('has_obj_permission:%s' % (request.method, ))
        user = request.user  # 获取用户User模型
        if not user.is_authenticated:
            return False
        authority = user.authority  # 获取权限模型
        if authority is None:
            return False
        number = authority.auth  # 获取权限数字
        for method, permissions in self.auth_number.items():  # 查找目标类型
            if permissions is not None and request.method == method:
                for item in permissions:  # 遍历目标类型的许可,这里的item是目标权限字符串
                    # 修复错误：在这个for循环之内不能returnFalse！否则会打破Or联结。
                    if item in auth_check.BELONG_AUTHORITY:  # 如果目标权限是从属权限
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


class User:
    class UserPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.UserManager, AuthorityName.Root)
        }

    class UserDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.UserManager, AuthorityName.Root),
            'PUT': (BelongName.IsSelf, AuthorityName.UserManager, AuthorityName.Root)
        }

    class StudentPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (AuthorityName.StudentManager, AuthorityName.Root)
        }

    class StudentDetailPermission(UserAuthorityPermission):
        auth_number = {
            'GET': (BelongName.IsSelf, BelongName.IsParent, AuthorityName.StudentManager, AuthorityName.Root),
            'PUT': (AuthorityName.StudentManager, AuthorityName.Root)
        }



