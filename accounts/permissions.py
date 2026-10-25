from django.contrib.auth.mixins import AccessMixin

from .models import User


class AdminRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.ADMIN:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class FacultyRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.FACULTY:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class StudentRequiredMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.STUDENT:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
