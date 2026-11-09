from django import forms
from django.utils import timezone

from .models import AttendanceConfig


class ClassSelectForm(forms.Form):
    assignment = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select subject and section",
    )
    date = forms.DateField(
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, assignments, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignment"].queryset = assignments
        self.fields["assignment"].label_from_instance = (
            lambda assignment: (
                f"{assignment.subject.code} - "
                f"{assignment.subject.name} "
                f"({assignment.section.name})"
            )
        )

    def clean_date(self):
        selected_date = self.cleaned_data["date"]
        if selected_date > timezone.localdate():
            raise forms.ValidationError(
                "Attendance cannot be marked for a future date."
            )
        return selected_date


class AttendanceConfigForm(forms.ModelForm):
    class Meta:
        model = AttendanceConfig
        fields = [
            "threshold_percentage",
            "correction_window_days",
            "term_start_date",
            "term_end_date",
        ]
        labels = {
            "threshold_percentage": "Minimum attendance percentage",
            "correction_window_days": "Attendance correction window (days)",
            "term_start_date": "Academic term start date",
            "term_end_date": "Academic term end date",
        }
        widgets = {
            "threshold_percentage": forms.NumberInput(
                attrs={"min": 0, "max": 100, "step": 1}
            ),
            "correction_window_days": forms.NumberInput(
                attrs={"min": 0, "max": 365, "step": 1}
            ),
            "term_start_date": forms.DateInput(attrs={"type": "date"}),
            "term_end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_threshold_percentage(self):
        value = self.cleaned_data["threshold_percentage"]
        if not 0 <= value <= 100:
            raise forms.ValidationError(
                "Enter a percentage between 0 and 100."
            )
        return value

    def clean_correction_window_days(self):
        value = self.cleaned_data["correction_window_days"]
        if not 0 <= value <= 365:
            raise forms.ValidationError(
                "Enter a correction window between 0 and 365 days."
            )
        return value

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("term_start_date")
        end_date = cleaned.get("term_end_date")
        if bool(start_date) != bool(end_date):
            raise forms.ValidationError(
                "Configure both the academic term start date and end date."
            )
        if start_date and end_date and start_date > end_date:
            self.add_error(
                "term_end_date",
                "The academic term end date must be on or after its start date.",
            )
        return cleaned
