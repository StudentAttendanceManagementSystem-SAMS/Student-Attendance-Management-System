from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from accounts.permissions import AdminRequiredMixin

from .forms import FacultyAssignmentForm, FacultyCreateForm, StudentCreateForm, StudentUpdateForm
from .models import Faculty, FacultyAssignment, Section, Student, Subject


class StudentListView(AdminRequiredMixin, ListView):
    model = Student
    template_name = "masterdata/student_list.html"
    context_object_name = "students"
    queryset = Student.objects.select_related("section").order_by("usn")


class StudentCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:student_list")
    success_message = "Student added."
    extra_context = {
        "title": "Add student",
        "cancel_url": reverse_lazy("masterdata:student_list"),
    }


class StudentUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:student_list")
    success_message = "Student updated."
    extra_context = {
        "title": "Edit student",
        "cancel_url": reverse_lazy("masterdata:student_list"),
    }


class SectionListView(AdminRequiredMixin, ListView):
    model = Section
    template_name = "masterdata/section_list.html"
    context_object_name = "sections"


class SectionCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Section
    fields = ["name", "semester", "academic_year"]
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:section_list")
    success_message = "Section added."
    extra_context = {
        "title": "Add section",
        "cancel_url": reverse_lazy("masterdata:section_list"),
    }


class SubjectListView(AdminRequiredMixin, ListView):
    model = Subject
    template_name = "masterdata/subject_list.html"
    context_object_name = "subjects"


class SubjectCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    fields = ["code", "name", "semester"]
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:subject_list")
    success_message = "Subject added."
    extra_context = {
        "title": "Add subject",
        "cancel_url": reverse_lazy("masterdata:subject_list"),
    }


class FacultyAssignmentListView(AdminRequiredMixin, ListView):
    model = FacultyAssignment
    template_name = "masterdata/assignment_list.html"
    context_object_name = "assignments"
    queryset = FacultyAssignment.objects.select_related("faculty", "subject", "section")


class FacultyAssignmentCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = FacultyAssignment
    form_class = FacultyAssignmentForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:assignment_list")
    success_message = "Assignment saved."
    extra_context = {
        "title": "Assign faculty",
        "cancel_url": reverse_lazy("masterdata:assignment_list"),
    }


class FacultyListView(AdminRequiredMixin, ListView):
    model = Faculty
    template_name = "masterdata/faculty_list.html"
    context_object_name = "faculty_members"


class FacultyCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Faculty
    form_class = FacultyCreateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:faculty_list")
    success_message = "Faculty added."
    extra_context = {
        "title": "Add faculty",
        "cancel_url": reverse_lazy("masterdata:faculty_list"),
    }
