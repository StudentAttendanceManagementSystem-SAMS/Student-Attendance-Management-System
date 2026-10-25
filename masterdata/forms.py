from django import forms
from django.db import transaction

from accounts.models import User

from .models import FacultyAssignment, Student


class StudentCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = Student
        fields = ["usn", "name", "section", "semester", "contact_no"]
        error_messages = {
            "usn": {"unique": "A student with this USN already exists."},
        }

    def clean_usn(self):
        usn = self.cleaned_data["usn"].strip().upper()
        if User.objects.filter(username=usn).exists():
            raise forms.ValidationError("A user account with this USN already exists.")
        return usn

    @transaction.atomic
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["usn"],
            password=self.cleaned_data["password"],
            role=User.STUDENT,
        )
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
        return student


class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["name", "section", "semester", "contact_no"]



class FacultyAssignmentForm(forms.ModelForm):
    class Meta:
        model = FacultyAssignment
        fields = ["faculty", "subject", "section"]
