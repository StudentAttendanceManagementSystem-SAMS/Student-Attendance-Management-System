from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from accounts.permissions import AdminRequiredMixin
from .forms import (
    FacultyAssignmentForm, FacultyCreateForm, FacultyUpdateForm,
    StudentCreateForm, StudentUpdateForm, SubjectForm,
)
from .models import Faculty, FacultyAssignment, Section, Student, Subject


class StudentListView(AdminRequiredMixin, ListView):
    model = Student
    template_name = "masterdata/student_list.html"
    context_object_name = "students"

    def get_queryset(self):
        qs = Student.objects.select_related("section", "user").order_by("usn")
        section = self.request.GET.get("section")
        semester = self.request.GET.get("semester")
        if section:
            qs = qs.filter(section_id=section)
        if semester:
            qs = qs.filter(semester=semester)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sections"] = Section.objects.order_by("name")
        context["selected_section"] = self.request.GET.get("section", "")
        context["selected_semester"] = self.request.GET.get("semester", "")
        context["semesters"] = range(1, 9)
        return context


class StudentCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Student
    form_class = StudentCreateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:student_list")
    success_message = "Student added."
    extra_context = {"title": "Add student", "cancel_url": reverse_lazy("masterdata:student_list")}


class StudentUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Student
    form_class = StudentUpdateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:student_list")
    success_message = "Student updated."
    extra_context = {"title": "Edit student", "cancel_url": reverse_lazy("masterdata:student_list")}


class StudentDeactivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        student = get_object_or_404(Student.objects.select_related("user"), pk=pk)
        student.user.is_active = False
        student.user.save(update_fields=["is_active"])
        messages.success(request, f"Student {student.usn} deactivated. Attendance history was retained.")
        return redirect("masterdata:student_list")


class SectionListView(AdminRequiredMixin, ListView):
    model = Section
    template_name = "masterdata/section_list.html"
    context_object_name = "sections"

    def get_queryset(self):
        from django.db.models import Count
        return Section.objects.annotate(student_count=Count("students")).order_by("name")


class SectionCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Section
    fields = ["name", "semester", "academic_year"]
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:section_list")
    success_message = "Section added."
    extra_context = {"title": "Add section", "cancel_url": reverse_lazy("masterdata:section_list")}


class SectionUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Section
    fields = ["name", "semester", "academic_year"]
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:section_list")
    success_message = "Section updated."
    extra_context = {"title": "Edit section", "cancel_url": reverse_lazy("masterdata:section_list")}


class SectionDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(Section, pk=pk)
        try:
            section.delete()
            messages.success(request, "Section deleted.")
        except ProtectedError:
            messages.error(request, "This section is in use and cannot be deleted. Reassign or retain its dependent records.")
        return redirect("masterdata:section_list")


class SubjectListView(AdminRequiredMixin, ListView):
    model = Subject
    template_name = "masterdata/subject_list.html"
    context_object_name = "subjects"
    queryset = Subject.objects.prefetch_related("section_links__section", "assignments__faculty").order_by("code")


class SubjectCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Subject
    form_class = SubjectForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:subject_list")
    success_message = "Subject added."
    extra_context = {"title": "Add subject and map sections", "cancel_url": reverse_lazy("masterdata:subject_list")}


class SubjectUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Subject
    form_class = SubjectForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:subject_list")
    success_message = "Subject updated."
    extra_context = {"title": "Edit subject and section mapping", "cancel_url": reverse_lazy("masterdata:subject_list")}


class SubjectDeleteView(AdminRequiredMixin, View):
    def post(self, request, pk):
        subject = get_object_or_404(Subject, pk=pk)
        try:
            subject.delete()
            messages.success(request, "Subject deleted.")
        except ProtectedError:
            messages.error(request, "This subject is in use and cannot be deleted.")
        return redirect("masterdata:subject_list")


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
    extra_context = {"title": "Assign faculty", "cancel_url": reverse_lazy("masterdata:assignment_list")}


class FacultyListView(AdminRequiredMixin, ListView):
    model = Faculty
    template_name = "masterdata/faculty_list.html"
    context_object_name = "faculty_members"
    queryset = Faculty.objects.select_related("user").prefetch_related(
        "assignments__subject", "assignments__section"
    ).order_by("employee_id")


class FacultyCreateView(AdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = Faculty
    form_class = FacultyCreateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:faculty_list")
    success_message = "Faculty added."
    extra_context = {"title": "Add faculty", "cancel_url": reverse_lazy("masterdata:faculty_list")}


class FacultyUpdateView(AdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Faculty
    form_class = FacultyUpdateForm
    template_name = "masterdata/form.html"
    success_url = reverse_lazy("masterdata:faculty_list")
    success_message = "Faculty updated."
    extra_context = {"title": "Edit faculty", "cancel_url": reverse_lazy("masterdata:faculty_list")}


class FacultyDeactivateView(AdminRequiredMixin, View):
    def post(self, request, pk):
        faculty = get_object_or_404(Faculty.objects.select_related("user"), pk=pk)
        faculty.user.is_active = False
        faculty.user.save(update_fields=["is_active"])
        messages.success(request, f"Faculty {faculty.employee_id} deactivated. Assignment and attendance history was retained.")
        return redirect("masterdata:faculty_list")
