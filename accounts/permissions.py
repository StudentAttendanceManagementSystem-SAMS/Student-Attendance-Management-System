
from functools import wraps

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import User


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if request.user.role not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


class RoleRequiredMixin(LoginRequiredMixin):
    allowed_roles = ()

    def dispatch(self, request, *args, **kwargs):
        if (
            request.user.is_authenticated
            and request.user.role not in self.allowed_roles
        ):
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.ADMIN,)


class FacultyRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.FACULTY,)


class StudentRequiredMixin(RoleRequiredMixin):
    allowed_roles = (User.STUDENT,)

def faculty_owns_assignment(user, assignment):
    profile = getattr(user, "faculty_profile", None)
    return profile is not None and assignment.faculty_id == profile.pk


def student_owns_record(user, student):
    profile = getattr(user, "student_profile", None)
    return profile is not None and student.pk == profile.pk
