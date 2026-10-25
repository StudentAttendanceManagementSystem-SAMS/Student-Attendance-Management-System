from django import forms
from django.db import transaction

from accounts.models import User

from .models import Student


class StudentCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)

    class Meta:
        model = Student
        fields = ["usn", "name", "section", "semester", "contact_no"]

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
