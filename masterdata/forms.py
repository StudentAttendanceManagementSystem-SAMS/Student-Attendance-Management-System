from django import forms
from django.db import transaction

from accounts.models import User
from .models import Faculty, FacultyAssignment, Section, Student, Subject, SubjectSection


class StudentCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = Student
        fields = ["usn", "name", "section", "semester", "contact_no"]
        error_messages = {
            "usn": {
                "unique": "A student with this USN already exists.",
            },
        }

    def clean_usn(self):
        usn = self.cleaned_data["usn"].strip().upper()
        if User.objects.filter(username__iexact=usn).exists():
            raise forms.ValidationError("A user account with this USN already exists.")
        return usn

    @transaction.atomic
    def save(self, commit=True):
        student = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data["usn"],
            password=self.cleaned_data["password"],
            role=User.STUDENT,
        )
        student.user = user
        if commit:
            student.save()
        return student


class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "section", "semester", "contact_no"]


class FacultyCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = Faculty
        fields = ["employee_id", "name", "department", "contact_no"]

    def clean_employee_id(self):
        employee_id = self.cleaned_data["employee_id"].strip().upper()
        if User.objects.filter(username__iexact=employee_id).exists():
            raise forms.ValidationError("An account with this employee ID already exists.")
        return employee_id

    @transaction.atomic
    def save(self, commit=True):
        faculty = super().save(commit=False)
        user = User.objects.create_user(
            username=self.cleaned_data["employee_id"],
            password=self.cleaned_data["password"],
            role=User.FACULTY,
        )
        faculty.user = user
        if commit:
            faculty.save()
        return faculty


class FacultyUpdateForm(forms.ModelForm):
    class Meta:
        model = Faculty
        fields = ["name", "department", "contact_no"]


class FacultyAssignmentForm(forms.ModelForm):
    class Meta:
        model = FacultyAssignment
        fields = ["faculty", "subject", "section"]

    @transaction.atomic
    def save(self, commit=True):
        assignment = super().save(commit=False)
        SubjectSection.objects.get_or_create(
            subject=assignment.subject, section=assignment.section
        )
        if commit:
            assignment.save()
        return assignment


class SubjectForm(forms.ModelForm):
    sections = forms.ModelMultipleChoiceField(
        queryset=Section.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Select every section in which this subject is taught.",
    )

    class Meta:
        model = Subject
        fields = ["code", "name", "semester"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sections"].queryset = Section.objects.order_by("name")
        if self.instance and self.instance.pk and not self.is_bound:
            self.initial["sections"] = self.instance.section_links.values_list(
                "section_id", flat=True
            )

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()

    def clean(self):
        cleaned = super().clean()
        selected_sections = cleaned.get("sections")
        if self.instance and self.instance.pk and selected_sections is not None:
            assigned_section_ids = set(
                self.instance.assignments.values_list("section_id", flat=True)
            )
            selected_ids = {section.pk for section in selected_sections}
            if not assigned_section_ids.issubset(selected_ids):
                self.add_error(
                    "sections",
                    "A section cannot be unmapped while faculty assignments exist for it. "
                    "Remove or change those assignments first.",
                )
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        subject = super().save(commit=commit)
        if commit:
            SubjectSection.objects.filter(subject=subject).exclude(
                section__in=self.cleaned_data["sections"]
            ).delete()
            for section in self.cleaned_data["sections"]:
                SubjectSection.objects.get_or_create(subject=subject, section=section)
        return subject
