from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from masterdata.models import Student, Faculty
from .models import StudentProfile, FacultyProfile, AdminProfile


class ProfileFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "profile-input")


class StudentProfileForm(ProfileFormMixin, forms.ModelForm):
    email = forms.EmailField(required=False)
    contact_no = forms.CharField(max_length=15, required=False)

    class Meta:
        model = StudentProfile
        fields = [
            "date_of_birth", "address", "parent_name", "parent_relationship", "parent_email",
            "parent_contact_no",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, student, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = student.user.email
        self.fields["contact_no"].initial = student.contact_no

    def clean_date_of_birth(self):
        value = self.cleaned_data.get("date_of_birth")
        if value and value >= timezone.localdate():
            raise ValidationError("Date of birth must be in the past.")
        return value

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            self.student.user.email = self.cleaned_data["email"]
            self.student.user.save(update_fields=["email"])
            self.student.contact_no = self.cleaned_data["contact_no"]
            self.student.save(update_fields=["contact_no"])
        return profile


class FacultyProfileForm(ProfileFormMixin, forms.ModelForm):
    institutional_email = forms.EmailField(required=False)
    contact_no = forms.CharField(max_length=15, required=False)

    class Meta:
        model = FacultyProfile
        fields = ["date_of_birth", "personal_email", "address"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "date_of_joining": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, faculty, **kwargs):
        self.faculty = faculty
        super().__init__(*args, **kwargs)
        self.fields["institutional_email"].initial = faculty.user.email
        self.fields["contact_no"].initial = faculty.contact_no

    def clean_date_of_birth(self):
        value = self.cleaned_data.get("date_of_birth")
        if value and value >= timezone.localdate():
            raise ValidationError("Date of birth must be in the past.")
        return value

    def clean(self):
        cleaned = super().clean()
        dob, joined = cleaned.get("date_of_birth"), cleaned.get("date_of_joining")
        if dob and joined and joined < dob:
            self.add_error("date_of_joining", "Joining date cannot be before date of birth.")
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            self.faculty.user.email = self.cleaned_data["institutional_email"]
            self.faculty.user.save(update_fields=["email"])
            self.faculty.contact_no = self.cleaned_data["contact_no"]
            self.faculty.save(update_fields=["contact_no"])
        return profile


class AdminProfileForm(ProfileFormMixin, forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = AdminProfile
        fields = ["date_of_birth", "date_of_joining", "designation", "contact_no", "address"]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "date_of_joining": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        self.fields["email"].initial = user.email

    def clean(self):
        cleaned = super().clean()
        dob, joined = cleaned.get("date_of_birth"), cleaned.get("date_of_joining")
        if dob and dob >= timezone.localdate():
            self.add_error("date_of_birth", "Date of birth must be in the past.")
        if dob and joined and joined < dob:
            self.add_error("date_of_joining", "Joining date cannot be before date of birth.")
        return cleaned

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            self.user.email = self.cleaned_data["email"]
            self.user.save(update_fields=["email"])
        return profile
