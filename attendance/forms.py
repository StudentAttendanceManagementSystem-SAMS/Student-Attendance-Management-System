
import datetime

from django import forms

from .models import AttendanceConfig


class ClassSelectForm(forms.Form):
    assignment = forms.ModelChoiceField(
        queryset=None,
        empty_label="Select subject and section",
    )
    date = forms.DateField(
        initial=datetime.date.today,
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def __init__(self, *args, assignments, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignment"].queryset = assignments
        self.fields["assignment"].label_from_instance = (
            lambda a: f"{a.subject.code} - {a.subject.name} ({a.section.name})"
        )


class AttendanceConfigForm(forms.ModelForm):
    class Meta:
        model = AttendanceConfig
        fields = ["threshold_percentage"]
        labels = {
            "threshold_percentage": "Minimum attendance percentage",
        }
        widgets = {
            "threshold_percentage": forms.NumberInput(
                attrs={"min": 0, "max": 100, "step": 1}
            ),
        }

    def clean_threshold_percentage(self):
        value = self.cleaned_data["threshold_percentage"]

        if not 0 <= value <= 100:
            raise forms.ValidationError(
                "Enter a percentage between 0 and 100."
            )

        return value
