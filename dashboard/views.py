from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from accounts.models import User


@login_required
def home(request):
    if request.user.role == User.STUDENT:
        return redirect("analytics:overall_attendance")
    elif request.user.role == User.FACULTY:
        return redirect("attendance:select_class")
    return redirect("masterdata:student_list")
