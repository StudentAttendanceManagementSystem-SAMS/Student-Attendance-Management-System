from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from accounts.models import User
from masterdata.models import Student, Faculty
from .forms import StudentProfileForm, FacultyProfileForm, AdminProfileForm
from .models import StudentProfile, FacultyProfile, AdminProfile


@login_required
def my_profile(request):
    user = request.user

    if user.role == User.STUDENT:
        student = Student.objects.select_related("user", "section").filter(user=user).first()
        if student is None:
            return render(request, "profiles/profile_missing.html", status=404)
        profile, _ = StudentProfile.objects.get_or_create(student=student)
        form = StudentProfileForm(
            request.POST or None, instance=profile, student=student
        )
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profiles:my_profile")
        return render(request, "profiles/student_profile.html", {
            "profile": profile, "student": student, "form": form,
        })

    if user.role == User.FACULTY:
        faculty = Faculty.objects.select_related("user").filter(user=user).first()
        if faculty is None:
            return render(request, "profiles/profile_missing.html", status=404)
        profile, _ = FacultyProfile.objects.get_or_create(faculty=faculty)
        form = FacultyProfileForm(
            request.POST or None, instance=profile, faculty=faculty
        )
        if request.method == "POST" and form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("profiles:my_profile")
        assignments = faculty.assignments.select_related("subject", "section")
        return render(request, "profiles/faculty_profile.html", {
            "profile": profile, "faculty": faculty, "form": form,
            "assignments": assignments,
        })

    profile, _ = AdminProfile.objects.get_or_create(user=user)
    form = AdminProfileForm(request.POST or None, instance=profile, user=user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profiles:my_profile")
    return render(request, "profiles/admin_profile.html", {
        "profile": profile, "form": form,
    })
