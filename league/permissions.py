from rest_framework import permissions


class TeamOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return view.action in ['update', 'destroy'] and obj.user == request.user


class PlayerOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return view.action in ['update', 'destroy'] and obj.team.user == request.user
