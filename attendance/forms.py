import datetime

from django import forms


class ClassSelectForm(forms.Form):
    assignment = forms.ModelChoiceField(queryset=None, empty_label="Select subject and section")
    date = forms.DateField(initial=datetime.date.today, widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, assignments, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assignment"].queryset = assignments
        self.fields["assignment"].label_from_instance = (
            lambda a: f"{a.subject.code} - {a.subject.name} ({a.section.name})"
        )
