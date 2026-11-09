from django import forms

from masterdata.models import Section, Subject


class DateRangeFilterForm(forms.Form):
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("date_from")
        end = cleaned.get("date_to")
        if start and end and start > end:
            raise forms.ValidationError("Start date must be on or before end date.")
        return cleaned


class FacultySubjectReportForm(DateRangeFilterForm):
    section = forms.ModelChoiceField(queryset=Section.objects.none(), required=True)
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), required=True)

    def __init__(self, *args, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.faculty = faculty
        if faculty is not None:
            assignments = faculty.assignments.select_related("section", "subject")
            self.fields["section"].queryset = Section.objects.filter(
                pk__in=assignments.values_list("section_id", flat=True)
            ).distinct().order_by("name")
            self.fields["subject"].queryset = Subject.objects.filter(
                pk__in=assignments.values_list("subject_id", flat=True)
            ).distinct().order_by("code")

    def clean(self):
        cleaned = super().clean()
        section = cleaned.get("section")
        subject = cleaned.get("subject")
        if section and subject:
            faculty = getattr(self, "faculty", None)
            if faculty and not faculty.assignments.filter(section=section, subject=subject).exists():
                raise forms.ValidationError("You are not assigned to this subject and section.")
        return cleaned


class StudentHistoryFilterForm(DateRangeFilterForm):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        required=False,
        empty_label="All current-semester subjects",
    )

    def __init__(self, *args, student=None, faculty=None, **kwargs):
        super().__init__(*args, **kwargs)
        if student is None:
            return
        subjects = Subject.objects.filter(semester=student.semester)
        if faculty is not None:
            subjects = subjects.filter(
                assignments__faculty=faculty,
                assignments__section=student.section,
            )
            self.fields["subject"].required = True
            self.fields["subject"].empty_label = None
        self.fields["subject"].queryset = subjects.distinct().order_by("code")
