from rest_framework import permissions


class RecipePermission(permissions.BasePermission):
    message = 'Редактировать рецепт могут только автор или админ.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        condition_1 = request.method in permissions.SAFE_METHODS
        condition_2 = request.user.is_superuser is True
        if condition_1 or condition_2:
            return True
        else:
            return obj.author == request.user


class SelfDataPermission(permissions.BasePermission):
    message = 'Редактировать данные могут только их владельцы и админ.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        condition_1 = request.method in permissions.SAFE_METHODS
        condition_2 = request.user.is_superuser is True
        if condition_1 or condition_2:
            return True
        else:
            return obj.user == request.user
